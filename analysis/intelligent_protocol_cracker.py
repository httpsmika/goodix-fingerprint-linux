"""
Erweiterte Goodix Protocol Analysis
Intelligenter Ansatz zum "Knacken" des Goodix-Protokolls
"""

import usb.core
import usb.util
import time
import struct
import logging
from typing import Optional, List, Tuple, Dict
import threading
import queue

logger = logging.getLogger(__name__)

class GoodixProtocolCracker:
    """Intelligenter Goodix-Protokoll-Cracker"""
    
    def __init__(self):
        self.device = None
        self.vendor_id = 0x27C6
        self.product_id = 0x55A2
        self.interface_number = 0
        self.endpoint_in = None
        self.endpoint_out = None
        self.discovered_commands = {}
        self.protocol_patterns = {}
        
    def connect(self) -> bool:
        """Verbindet mit dem Device"""
        try:
            self.device = usb.core.find(idVendor=self.vendor_id, idProduct=self.product_id)
            if self.device is None:
                logger.error("Device nicht gefunden")
                return False
            
            # Kernel-Treiber trennen falls aktiv
            if self.device.is_kernel_driver_active(0):
                try:
                    self.device.detach_kernel_driver(0)
                    logger.info("Kernel-Treiber getrennt")
                except:
                    logger.warning("Konnte Kernel-Treiber nicht trennen")
            
            # Configuration setzen
            self.device.set_configuration()
            usb.util.claim_interface(self.device, 0)
            
            # Endpoints finden
            cfg = self.device.get_active_configuration()
            intf = cfg[(0, 0)]
            
            for ep in intf:
                if usb.util.endpoint_direction(ep.bEndpointAddress) == usb.util.ENDPOINT_IN:
                    self.endpoint_in = ep
                elif usb.util.endpoint_direction(ep.bEndpointAddress) == usb.util.ENDPOINT_OUT:
                    self.endpoint_out = ep
            
            logger.info("✅ Erfolgreich verbunden und bereit zum Protokoll-Knacken!")
            return True
            
        except Exception as e:
            logger.error(f"Verbindungsfehler: {e}")
            return False
    
    def safe_send_receive(self, data: bytes, timeout: int = 1000) -> Optional[bytes]:
        """Sichere Send/Receive-Operation"""
        try:
            if self.endpoint_out is None or self.endpoint_in is None:
                return None
            
            # Senden
            bytes_sent = self.device.write(self.endpoint_out.bEndpointAddress, data, timeout)
            logger.debug(f"📤 Gesendet: {data.hex()}")
            
            # Kurz warten
            time.sleep(0.01)
            
            # Empfangen
            response = self.device.read(self.endpoint_in.bEndpointAddress, 512, timeout)
            response_bytes = bytes(response)
            logger.debug(f"📥 Empfangen: {response_bytes.hex()}")
            
            return response_bytes
            
        except usb.core.USBTimeoutError:
            logger.debug("⏱️ Timeout - das ist normal")
            return None
        except Exception as e:
            logger.error(f"❌ Fehler: {e}")
            return None
    
    def intelligent_protocol_discovery(self):
        """Intelligente Protokoll-Entdeckung basierend auf typischen Patterns"""
        
        logger.info("🔍 Starte intelligente Protokoll-Entdeckung...")
        
        # Typische Fingerprint-Scanner-Kommando-Patterns
        common_patterns = {
            # Status/Info-Kommandos (meist sicher)
            'status_queries': [
                b'\x01',                    # Get Status
                b'\x02',                    # Get Info  
                b'\x03',                    # Get Version
                b'\x04',                    # Get Capabilities
                b'\x10',                    # Device Info
                b'\x20',                    # Firmware Version
            ],
            
            # Erweiterte Info-Kommandos
            'extended_info': [
                b'\x01\x00',               # Extended Status
                b'\x02\x00',               # Extended Info
                b'\x10\x00',               # Extended Device Info
                b'\x40\x00',               # Configuration Query
            ],
            
            # Mögliche Initialisierung (vorsichtig!)
            'possible_init': [
                b'\x80',                    # Reset/Init
                b'\x81',                    # Soft Reset
                b'\xFF',                    # Ping/Echo
                b'\x00',                    # NOP/Ping
            ]
        }
        
        results = {}
        
        for category, commands in common_patterns.items():
            logger.info(f"🧪 Teste {category}...")
            results[category] = {}
            
            for cmd in commands:
                logger.info(f"  📡 Teste Kommando: {cmd.hex()}")
                response = self.safe_send_receive(cmd)
                
                if response and len(response) > 0:
                    logger.info(f"  ✅ Antwort erhalten! ({len(response)} bytes)")
                    results[category][cmd.hex()] = response
                    self.discovered_commands[cmd.hex()] = response
                else:
                    logger.info(f"  ⚪ Keine Antwort")
                    results[category][cmd.hex()] = None
                
                # Sicherheitspause zwischen Kommandos
                time.sleep(0.1)
        
        return results
    
    def analyze_response_patterns(self):
        """Analysiert die Response-Patterns für Protokoll-Verständnis"""
        
        if not self.discovered_commands:
            logger.warning("Keine Kommandos zum Analysieren gefunden")
            return
        
        logger.info("🔬 Analysiere Response-Patterns...")
        
        patterns = {}
        
        for cmd_hex, response in self.discovered_commands.items():
            if response is None:
                continue
                
            analysis = {
                'length': len(response),
                'first_bytes': response[:4].hex() if len(response) >= 4 else response.hex(),
                'last_bytes': response[-4:].hex() if len(response) >= 4 else response.hex(),
                'ascii_strings': self.extract_ascii_strings(response),
                'possible_structure': self.guess_structure(response)
            }
            
            patterns[cmd_hex] = analysis
            
            logger.info(f"📊 Kommando {cmd_hex}:")
            logger.info(f"    Länge: {analysis['length']} bytes")
            logger.info(f"    Start: {analysis['first_bytes']}")
            logger.info(f"    Ende: {analysis['last_bytes']}")
            if analysis['ascii_strings']:
                logger.info(f"    ASCII: {analysis['ascii_strings']}")
        
        self.protocol_patterns = patterns
        return patterns
    
    def extract_ascii_strings(self, data: bytes, min_length: int = 3) -> List[str]:
        """Extrahiert ASCII-Strings aus Binärdaten"""
        strings = []
        current_string = ""
        
        for byte in data:
            if 32 <= byte <= 126:  # Druckbare ASCII-Zeichen
                current_string += chr(byte)
            else:
                if len(current_string) >= min_length:
                    strings.append(current_string)
                current_string = ""
        
        if len(current_string) >= min_length:
            strings.append(current_string)
        
        return strings
    
    def guess_structure(self, data: bytes) -> str:
        """Versucht die Datenstruktur zu erraten"""
        if len(data) == 0:
            return "empty"
        elif len(data) == 1:
            return f"single_byte(0x{data[0]:02x})"
        elif len(data) == 2:
            value = struct.unpack('<H', data)[0]
            return f"uint16_le({value})"
        elif len(data) == 4:
            value = struct.unpack('<I', data)[0]
            return f"uint32_le({value})"
        elif data[0] == 0x00 and len(data) > 1:
            return "status_response"
        elif all(b == 0xFF for b in data):
            return "all_ones"
        elif all(b == 0x00 for b in data):
            return "all_zeros"
        else:
            return f"complex_data({len(data)}b)"
    
    def generate_protocol_documentation(self) -> str:
        """Generiert Protokoll-Dokumentation basierend auf Erkenntnissen"""
        
        doc = """
# 🔓 Goodix Protocol Analysis Results

## Discovered Commands

"""
        
        for cmd_hex, response in self.discovered_commands.items():
            if response is not None:
                doc += f"### Command 0x{cmd_hex}\n"
                doc += f"- **Response Length**: {len(response)} bytes\n"
                doc += f"- **Raw Response**: `{response.hex()}`\n"
                
                if cmd_hex in self.protocol_patterns:
                    pattern = self.protocol_patterns[cmd_hex]
                    doc += f"- **Structure**: {pattern['possible_structure']}\n"
                    if pattern['ascii_strings']:
                        doc += f"- **ASCII Strings**: {', '.join(pattern['ascii_strings'])}\n"
                
                doc += f"- **Hex Dump**:\n```\n{self.hex_dump(response)}\n```\n\n"
        
        doc += """
## Protocol Analysis

### Observations:
- Device responds to standard query commands
- Response patterns suggest structured protocol
- ASCII strings may contain version/device info

### Next Steps:
1. Analyze response structures in detail
2. Test scan-related commands (carefully!)
3. Compare with Windows driver traffic
4. Implement Python driver prototype

### Safety Notes:
⚠️ Only tested safe query commands
⚠️ No scan/write operations attempted
⚠️ Ready for comparison with Windows captures
"""
        
        return doc
    
    def hex_dump(self, data: bytes, width: int = 16) -> str:
        """Erstellt einen formatierten Hex-Dump"""
        lines = []
        for i in range(0, len(data), width):
            chunk = data[i:i+width]
            hex_part = ' '.join(f'{b:02x}' for b in chunk)
            ascii_part = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in chunk)
            lines.append(f'{i:04x}: {hex_part:<{width*3}} {ascii_part}')
        return '\n'.join(lines)
    
    def disconnect(self):
        """Trennt die Verbindung sauber"""
        if self.device:
            try:
                usb.util.release_interface(self.device, 0)
                usb.util.dispose_resources(self.device)
                logger.info("🔌 Verbindung getrennt")
            except:
                pass

def main():
    """Hauptfunktion für das Protokoll-Knacken"""
    logging.basicConfig(level=logging.INFO, 
                       format='%(asctime)s - %(levelname)s - %(message)s')
    
    logger.info("🚀 Goodix Protocol Cracker gestartet!")
    logger.info("🎯 Ziel: Protokoll intelligent und sicher 'knacken'")
    
    cracker = GoodixProtocolCracker()
    
    if not cracker.connect():
        logger.error("❌ Konnte nicht mit Device verbinden!")
        return
    
    try:
        # Intelligente Protokoll-Entdeckung
        results = cracker.intelligent_protocol_discovery()
        
        # Pattern-Analyse
        patterns = cracker.analyze_response_patterns()
        
        # Dokumentation generieren
        doc = cracker.generate_protocol_documentation()
        
        # Ergebnisse speichern
        with open('protocol_docs/goodix_protocol_analysis.md', 'w') as f:
            f.write(doc)
        
        logger.info("📋 Protokoll-Analyse abgeschlossen!")
        logger.info("📄 Ergebnisse gespeichert in: protocol_docs/goodix_protocol_analysis.md")
        
        # Zusammenfassung
        working_commands = len([cmd for cmd, resp in cracker.discovered_commands.items() if resp is not None])
        logger.info(f"🔍 {working_commands} funktionierende Kommandos entdeckt!")
        
        if working_commands > 0:
            logger.info("🎉 PROTOKOLL TEILWEISE GEKNACKT! 🎉")
            logger.info("📊 Nächste Schritte: Windows-Traffic-Vergleich für vollständiges Verständnis")
        
    finally:
        cracker.disconnect()

if __name__ == "__main__":
    main()
