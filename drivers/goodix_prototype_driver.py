"""
Goodix Fingerprint Driver Prototype
Vollständiger Python-Prototyp für den Goodix-Sensor basierend auf RE-Erkenntnissen
"""

import usb.core
import usb.util
import time
import threading
import queue
import struct
from typing import Optional, Tuple, List, Dict, Callable
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class GoodixStatus(Enum):
    """Goodix Device Status Codes"""
    OK = 0x00
    ERROR = 0x01
    BUSY = 0x02
    NOT_READY = 0x03
    TIMEOUT = 0x04
    NO_FINGER = 0x05
    FINGER_DETECTED = 0x06

class GoodixCommand(Enum):
    """Goodix Protocol Commands (Based on RE Analysis)"""
    STATUS = 0x01
    DEVICE_INFO = 0x02
    FIRMWARE_VERSION = 0x03
    INITIALIZE = 0x10
    START_SCAN = 0x20
    SCAN_STATUS = 0x21
    READ_IMAGE = 0x30
    CONFIG_QUERY = 0x40
    RESET = 0x80
    ECHO = 0xFF

class GoodixFingerprintDriver:
    """
    Goodix Fingerprint Sensor Driver Prototype
    
    Implementiert das reverse-engineerte Protokoll für den 27C6:55A2 Sensor
    """
    
    def __init__(self, vendor_id: int = 0x27C6, product_id: int = 0x55A2):
        self.vendor_id = vendor_id
        self.product_id = product_id
        self.device: Optional[usb.core.Device] = None
        self.interface_number = 0
        self.endpoint_in = None
        self.endpoint_out = None
        self.is_connected = False
        self.is_initialized = False
        
        # Callback für Events
        self.on_finger_detected: Optional[Callable] = None
        self.on_scan_complete: Optional[Callable] = None
        self.on_error: Optional[Callable] = None
        
        # Scan-Monitoring
        self._scan_thread = None
        self._scan_active = False
        
    def connect(self) -> bool:
        """Verbindet mit dem Goodix-Device"""
        try:
            logger.info(f"🔍 Suche nach Goodix-Device {self.vendor_id:04X}:{self.product_id:04X}")
            
            self.device = usb.core.find(idVendor=self.vendor_id, idProduct=self.product_id)
            if self.device is None:
                logger.error("❌ Device nicht gefunden")
                return False
            
            # Kernel-Treiber-Handling
            try:
                if self.device.is_kernel_driver_active(0):
                    self.device.detach_kernel_driver(0)
                    logger.info("🔌 Kernel-Treiber getrennt")
            except Exception as e:
                logger.warning(f"⚠️ Kernel-Treiber-Trennung fehlgeschlagen: {e}")
            
            # Device konfigurieren
            self.device.set_configuration()
            usb.util.claim_interface(self.device, 0)
            
            # Endpoints finden
            self._find_endpoints()
            
            self.is_connected = True
            logger.info("✅ Erfolgreich mit Goodix-Device verbunden")
            return True
            
        except Exception as e:
            logger.error(f"❌ Verbindungsfehler: {e}")
            return False
    
    def _find_endpoints(self):
        """Findet und konfiguriert die USB-Endpoints"""
        cfg = self.device.get_active_configuration()
        intf = cfg[(0, 0)]
        
        for ep in intf:
            if usb.util.endpoint_direction(ep.bEndpointAddress) == usb.util.ENDPOINT_IN:
                self.endpoint_in = ep
                logger.debug(f"📥 IN Endpoint: 0x{ep.bEndpointAddress:02x}")
            elif usb.util.endpoint_direction(ep.bEndpointAddress) == usb.util.ENDPOINT_OUT:
                self.endpoint_out = ep
                logger.debug(f"📤 OUT Endpoint: 0x{ep.bEndpointAddress:02x}")
    
    def _send_command(self, command: GoodixCommand, data: bytes = b'', timeout: int = 1000) -> Optional[bytes]:
        """Sendet ein Kommando und wartet auf Antwort"""
        if not self.is_connected:
            logger.error("❌ Device nicht verbunden")
            return None
        
        try:
            # Kommando-Paket erstellen
            cmd_byte = command.value if isinstance(command, GoodixCommand) else command
            packet = bytes([cmd_byte]) + data
            
            logger.debug(f"📤 Sende: {packet.hex()}")
            
            # Senden
            bytes_sent = self.device.write(self.endpoint_out.bEndpointAddress, packet, timeout)
            
            # Kurze Pause für Device-Processing
            time.sleep(0.01)
            
            # Antwort empfangen
            response = self.device.read(self.endpoint_in.bEndpointAddress, 512, timeout)
            response_bytes = bytes(response)
            
            logger.debug(f"📥 Empfangen: {response_bytes.hex()}")
            return response_bytes
            
        except usb.core.USBTimeoutError:
            logger.debug("⏱️ USB-Timeout")
            return None
        except Exception as e:
            logger.error(f"❌ Kommando-Fehler: {e}")
            return None
    
    def initialize(self) -> bool:
        """Initialisiert den Sensor"""
        if not self.is_connected:
            logger.error("❌ Device nicht verbunden")
            return False
        
        logger.info("🔧 Initialisiere Goodix-Sensor...")
        
        # 1. Device-Status prüfen
        status_response = self._send_command(GoodixCommand.STATUS)
        if status_response is None:
            logger.error("❌ Status-Abfrage fehlgeschlagen")
            return False
        
        logger.info(f"📊 Device-Status: {status_response.hex()}")
        
        # 2. Device-Informationen abrufen
        info_response = self._send_command(GoodixCommand.DEVICE_INFO)
        if info_response:
            logger.info(f"ℹ️ Device-Info: {info_response.hex()}")
        
        # 3. Firmware-Version abrufen
        version_response = self._send_command(GoodixCommand.FIRMWARE_VERSION)
        if version_response:
            logger.info(f"🔧 Firmware: {version_response.hex()}")
        
        # 4. Sensor initialisieren
        init_response = self._send_command(GoodixCommand.INITIALIZE)
        if init_response is None:
            logger.error("❌ Sensor-Initialisierung fehlgeschlagen")
            return False
        
        # Response analysieren
        if len(init_response) > 0 and init_response[0] == GoodixStatus.OK.value:
            self.is_initialized = True
            logger.info("✅ Sensor erfolgreich initialisiert")
            return True
        else:
            logger.error(f"❌ Initialisierung fehlgeschlagen: {init_response.hex()}")
            return False
    
    def start_scan(self) -> bool:
        """Startet einen Fingerabdruck-Scan"""
        if not self.is_initialized:
            logger.error("❌ Sensor nicht initialisiert")
            return False
        
        logger.info("👆 Starte Fingerabdruck-Scan...")
        
        # Scan-Kommando senden
        scan_response = self._send_command(GoodixCommand.START_SCAN)
        if scan_response is None:
            logger.error("❌ Scan-Start fehlgeschlagen")
            return False
        
        if len(scan_response) > 0 and scan_response[0] == GoodixStatus.OK.value:
            logger.info("✅ Scan gestartet - Finger auflegen!")
            
            # Scan-Monitoring in separatem Thread
            self._scan_active = True
            self._scan_thread = threading.Thread(target=self._monitor_scan)
            self._scan_thread.start()
            
            return True
        else:
            logger.error(f"❌ Scan-Start fehlgeschlagen: {scan_response.hex()}")
            return False
    
    def _monitor_scan(self):
        """Monitort den Scan-Fortschritt"""
        while self._scan_active:
            try:
                # Scan-Status abfragen
                status_response = self._send_command(GoodixCommand.SCAN_STATUS)
                
                if status_response and len(status_response) > 0:
                    status = status_response[0]
                    
                    if status == GoodixStatus.FINGER_DETECTED.value:
                        logger.info("👆 Finger erkannt!")
                        if self.on_finger_detected:
                            self.on_finger_detected()
                    
                    elif status == GoodixStatus.OK.value:
                        logger.info("✅ Scan abgeschlossen!")
                        self._scan_complete()
                        break
                    
                    elif status == GoodixStatus.NO_FINGER.value:
                        logger.debug("⏳ Warte auf Finger...")
                
                time.sleep(0.1)  # 100ms Polling-Intervall
                
            except Exception as e:
                logger.error(f"❌ Scan-Monitoring-Fehler: {e}")
                break
    
    def _scan_complete(self):
        """Behandelt abgeschlossenen Scan"""
        self._scan_active = False
        
        # Versuche Bilddaten zu lesen
        image_data = self._send_command(GoodixCommand.READ_IMAGE)
        
        if image_data and len(image_data) > 1:
            logger.info(f"🖼️ Bilddaten empfangen: {len(image_data)} bytes")
            
            if self.on_scan_complete:
                self.on_scan_complete(image_data)
        else:
            logger.warning("⚠️ Keine Bilddaten empfangen")
    
    def stop_scan(self):
        """Stoppt den aktuellen Scan"""
        self._scan_active = False
        if self._scan_thread and self._scan_thread.is_alive():
            self._scan_thread.join(timeout=1.0)
        logger.info("⏹️ Scan gestoppt")
    
    def get_device_info(self) -> Dict[str, any]:
        """Sammelt umfassende Device-Informationen"""
        if not self.is_connected:
            return {}
        
        info = {
            'vendor_id': self.vendor_id,
            'product_id': self.product_id,
            'connected': self.is_connected,
            'initialized': self.is_initialized
        }
        
        # Status abrufen
        status_response = self._send_command(GoodixCommand.STATUS)
        if status_response:
            info['status_raw'] = status_response.hex()
            if len(status_response) > 0:
                info['status'] = GoodixStatus(status_response[0]).name
        
        # Device-Info abrufen
        device_response = self._send_command(GoodixCommand.DEVICE_INFO)
        if device_response:
            info['device_info_raw'] = device_response.hex()
        
        # Firmware-Version abrufen
        version_response = self._send_command(GoodixCommand.FIRMWARE_VERSION)
        if version_response:
            info['firmware_raw'] = version_response.hex()
        
        return info
    
    def disconnect(self):
        """Trennt die Verbindung sauber"""
        if self._scan_active:
            self.stop_scan()
        
        if self.device:
            try:
                usb.util.release_interface(self.device, 0)
                usb.util.dispose_resources(self.device)
                logger.info("🔌 Verbindung getrennt")
            except:
                pass
        
        self.is_connected = False
        self.is_initialized = False

def demo_driver():
    """Demo-Anwendung für den Goodix-Treiber"""
    logging.basicConfig(level=logging.INFO, 
                       format='%(asctime)s - %(levelname)s - %(message)s')
    
    print("🚀 Goodix Fingerprint Driver Demo")
    print("=" * 40)
    
    driver = GoodixFingerprintDriver()
    
    # Event-Callbacks definieren
    def on_finger_detected():
        print("👆 FINGER ERKANNT - Bitte ruhig halten...")
    
    def on_scan_complete(image_data):
        print(f"✅ SCAN ABGESCHLOSSEN - {len(image_data)} bytes Bilddaten")
        print(f"📊 Erste 32 bytes: {image_data[:32].hex()}")
    
    def on_error(error):
        print(f"❌ FEHLER: {error}")
    
    driver.on_finger_detected = on_finger_detected
    driver.on_scan_complete = on_scan_complete
    driver.on_error = on_error
    
    try:
        # Verbinden
        if not driver.connect():
            print("❌ Konnte nicht mit Device verbinden!")
            return
        
        # Device-Informationen anzeigen
        info = driver.get_device_info()
        print("\\n📋 Device-Informationen:")
        for key, value in info.items():
            print(f"  {key}: {value}")
        
        # Initialisieren
        if not driver.initialize():
            print("❌ Sensor-Initialisierung fehlgeschlagen!")
            return
        
        # Interactive Scan
        print("\\n🎯 Bereit für Fingerabdruck-Scans!")
        print("Befehle: 'scan' = Scan starten, 'info' = Device-Info, 'quit' = Beenden")
        
        while True:
            try:
                cmd = input("\\n> ").strip().lower()
                
                if cmd == 'quit':
                    break
                elif cmd == 'scan':
                    driver.start_scan()
                elif cmd == 'info':
                    info = driver.get_device_info()
                    for key, value in info.items():
                        print(f"  {key}: {value}")
                elif cmd == 'stop':
                    driver.stop_scan()
                else:
                    print("Unbekannter Befehl. Verwende: scan, info, stop, quit")
                    
            except KeyboardInterrupt:
                break
    
    finally:
        driver.disconnect()
        print("\\n👋 Demo beendet")

if __name__ == "__main__":
    demo_driver()
