"""
USB Protocol Analyzer für Goodix Fingerprint Sensor

Dieses Modul implementiert grundlegende USB-Kommunikation und 
Protokoll-Analyse für den Goodix-Sensor.
"""

import usb.core
import usb.util
import time
import logging
from typing import Optional, List, Tuple

logger = logging.getLogger(__name__)

class GoodixProtocolAnalyzer:
    """Analysiert und implementiert das Goodix USB-Protokoll"""
    
    def __init__(self, vendor_id: int = 0x27C6, product_id: int = 0x55A2):
        self.vendor_id = vendor_id
        self.product_id = product_id
        self.device: Optional[usb.core.Device] = None
        self.interface_number = 0
        self.endpoint_in = None
        self.endpoint_out = None
        
    def connect(self) -> bool:
        """Verbindet mit dem Goodix-Device"""
        try:
            self.device = usb.core.find(idVendor=self.vendor_id, idProduct=self.product_id)
            
            if self.device is None:
                logger.error("Device nicht gefunden")
                return False
            
            # Device konfigurieren
            if self.device.is_kernel_driver_active(self.interface_number):
                logger.info("Kernel-Treiber trennen...")
                self.device.detach_kernel_driver(self.interface_number)
            
            # Configuration setzen
            self.device.set_configuration()
            
            # Interface claimen
            usb.util.claim_interface(self.device, self.interface_number)
            
            # Endpoints finden
            self._find_endpoints()
            
            logger.info("Erfolgreich mit Goodix-Device verbunden")
            return True
            
        except Exception as e:
            logger.error(f"Fehler beim Verbinden: {e}")
            return False
    
    def _find_endpoints(self):
        """Findet die In- und Out-Endpoints"""
        cfg = self.device.get_active_configuration()
        intf = cfg[(self.interface_number, 0)]
        
        for ep in intf:
            if usb.util.endpoint_direction(ep.bEndpointAddress) == usb.util.ENDPOINT_IN:
                self.endpoint_in = ep
                logger.info(f"IN Endpoint gefunden: 0x{ep.bEndpointAddress:02x}")
            elif usb.util.endpoint_direction(ep.bEndpointAddress) == usb.util.ENDPOINT_OUT:
                self.endpoint_out = ep
                logger.info(f"OUT Endpoint gefunden: 0x{ep.bEndpointAddress:02x}")
    
    def send_command(self, data: bytes, timeout: int = 1000) -> bool:
        """Sendet ein Kommando an das Device"""
        if self.endpoint_out is None:
            logger.error("Kein OUT-Endpoint verfügbar")
            return False
        
        try:
            logger.debug(f"Sende: {data.hex()}")
            bytes_written = self.device.write(self.endpoint_out.bEndpointAddress, data, timeout)
            logger.debug(f"{bytes_written} Bytes gesendet")
            return True
        except Exception as e:
            logger.error(f"Fehler beim Senden: {e}")
            return False
    
    def read_response(self, size: int = 64, timeout: int = 1000) -> Optional[bytes]:
        """Liest eine Antwort vom Device"""
        if self.endpoint_in is None:
            logger.error("Kein IN-Endpoint verfügbar")
            return None
        
        try:
            data = self.device.read(self.endpoint_in.bEndpointAddress, size, timeout)
            response = bytes(data)
            logger.debug(f"Empfangen: {response.hex()}")
            return response
        except usb.core.USBTimeoutError:
            logger.debug("Timeout beim Lesen")
            return None
        except Exception as e:
            logger.error(f"Fehler beim Lesen: {e}")
            return None
    
    def send_and_receive(self, command: bytes, response_size: int = 64, timeout: int = 1000) -> Optional[bytes]:
        """Sendet ein Kommando und wartet auf Antwort"""
        if not self.send_command(command, timeout):
            return None
        
        time.sleep(0.01)  # Kurze Pause
        return self.read_response(response_size, timeout)
    
    def probe_commands(self):
        """Probiert verschiedene Kommandos aus (Vorsicht!)"""
        logger.warning("Starte Kommando-Probing - das kann das Device beschädigen!")
        
        # Typische Fingerprint-Scanner-Kommandos
        test_commands = [
            b'\x01',  # Häufig verwendet für "Get Status"
            b'\x02',  # Initialization
            b'\x03',  # Get Version
            b'\x10',  # Start Scan
            b'\x20',  # Stop Scan
            b'\x40\x00\x00\x00',  # Extended command
            b'\x80',  # Reset
        ]
        
        results = []
        
        for cmd in test_commands:
            logger.info(f"Teste Kommando: {cmd.hex()}")
            response = self.send_and_receive(cmd)
            
            if response:
                logger.info(f"Antwort erhalten: {response.hex()}")
                results.append((cmd, response))
            else:
                logger.info("Keine Antwort")
                results.append((cmd, None))
            
            time.sleep(0.1)  # Pause zwischen Kommandos
        
        return results
    
    def disconnect(self):
        """Trennt die Verbindung zum Device"""
        if self.device:
            try:
                usb.util.release_interface(self.device, self.interface_number)
                usb.util.dispose_resources(self.device)
                logger.info("Verbindung getrennt")
            except Exception as e:
                logger.error(f"Fehler beim Trennen: {e}")

def hex_dump(data: bytes, width: int = 16) -> str:
    """Erstellt einen Hex-Dump einer Byte-Sequenz"""
    lines = []
    for i in range(0, len(data), width):
        chunk = data[i:i+width]
        hex_part = ' '.join(f'{b:02x}' for b in chunk)
        ascii_part = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in chunk)
        lines.append(f'{i:04x}: {hex_part:<{width*3}} {ascii_part}')
    return '\n'.join(lines)

def main():
    """Test-Funktion"""
    logging.basicConfig(level=logging.INFO)
    
    analyzer = GoodixProtocolAnalyzer()
    
    if analyzer.connect():
        print("Verbunden! Starte Protokoll-Analyse...")
        
        # Vorsichtige Analyse
        results = analyzer.probe_commands()
        
        print("\n=== Kommando-Analyse Ergebnisse ===")
        for cmd, response in results:
            print(f"\nKommando: {cmd.hex()}")
            if response:
                print(f"Antwort ({len(response)} bytes):")
                print(hex_dump(response))
            else:
                print("Keine Antwort")
        
        analyzer.disconnect()
    else:
        print("Konnte nicht mit Device verbinden!")

if __name__ == "__main__":
    main()
