#!/usr/bin/env python3
'''
USB PCAP Analyzer für Goodix Fingerprint Sensor

Analysiert Windows USB-Captures und extrahiert Protokoll-Information.
'''

import sys
try:
    from scapy.all import *
    from scapy.layers.usb import *
except ImportError:
    print("Scapy ist nicht installiert. Installieren mit:")
    print("pip3 install scapy")
    sys.exit(1)

class GoodixUSBAnalyzer:
    def __init__(self, pcap_file):
        self.pcap_file = pcap_file
        self.packets = []
        self.goodix_packets = []
        
    def load_pcap(self):
        '''Lädt PCAP-Datei'''
        try:
            self.packets = rdpcap(self.pcap_file)
            print(f"✓ {len(self.packets)} Pakete geladen aus {self.pcap_file}")
        except Exception as e:
            print(f"✗ Fehler beim Laden: {e}")
            return False
        return True
    
    def filter_goodix_traffic(self):
        '''Filtert Goodix-spezifischen Traffic'''
        for packet in self.packets:
            if hasattr(packet, 'load'):
                # USB-spezifische Filterung hier
                self.goodix_packets.append(packet)
        
        print(f"✓ {len(self.goodix_packets)} Goodix-Pakete gefiltert")
    
    def analyze_commands(self):
        '''Analysiert Kommando-Patterns'''
        commands = {}
        
        for packet in self.goodix_packets:
            if hasattr(packet, 'load'):
                data = bytes(packet.load)
                if len(data) > 0:
                    cmd = data[0]
                    if cmd not in commands:
                        commands[cmd] = []
                    commands[cmd].append(data)
        
        print("\n=== Erkannte Kommandos ===")
        for cmd, packets in commands.items():
            print(f"Kommando 0x{cmd:02X}: {len(packets)} Pakete")
            if packets:
                print(f"  Beispiel: {packets[0].hex()}")
    
    def hex_dump_packets(self, limit=10):
        '''Gibt Hex-Dumps der ersten Pakete aus'''
        print(f"\n=== Erste {limit} Pakete ===")
        
        for i, packet in enumerate(self.goodix_packets[:limit]):
            if hasattr(packet, 'load'):
                data = bytes(packet.load)
                print(f"\nPaket {i+1} ({len(data)} bytes):")
                print(self.hex_dump(data))
    
    def hex_dump(self, data, width=16):
        '''Erstellt Hex-Dump'''
        lines = []
        for i in range(0, len(data), width):
            chunk = data[i:i+width]
            hex_part = ' '.join(f'{b:02x}' for b in chunk)
            ascii_part = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in chunk)
            lines.append(f'{i:04x}: {hex_part:<{width*3}} {ascii_part}')
        return '\n'.join(lines)

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 analyze_usb_capture.py <pcap_file>")
        sys.exit(1)
    
    pcap_file = sys.argv[1]
    analyzer = GoodixUSBAnalyzer(pcap_file)
    
    if analyzer.load_pcap():
        analyzer.filter_goodix_traffic()
        analyzer.analyze_commands()
        analyzer.hex_dump_packets()

if __name__ == "__main__":
    main()
