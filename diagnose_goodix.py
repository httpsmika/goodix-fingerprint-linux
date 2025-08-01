#!/usr/bin/env python3
"""
Goodix Sensor Diagnose-Tool
Schnelle Überprüfung des Sensor-Status und USB-Berechtigungen
"""

import sys
import os
import subprocess
import pwd
import grp
from drivers.goodix_prototype_driver import GoodixFingerprintDriver
import logging

# Logging für Diagnose
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class GoodixDiagnostics:
    """Diagnose-Tool für Goodix-Sensor"""
    
    def __init__(self):
        self.user = pwd.getpwuid(os.getuid()).pw_name
        self.uid = os.getuid()
        
    def check_user_permissions(self):
        """Prüft Benutzer-Berechtigungen"""
        print("👤 Benutzer-Berechtigungen:")
        print(f"   Aktueller Benutzer: {self.user} (UID: {self.uid})")
        
        # Gruppen prüfen
        groups = [grp.getgrgid(gid).gr_name for gid in os.getgroups()]
        print(f"   Gruppen: {', '.join(groups)}")
        
        # Wichtige Gruppen für USB-Zugriff
        usb_groups = ['plugdev', 'dialout', 'users']
        missing_groups = [g for g in usb_groups if g not in groups]
        
        if missing_groups:
            print(f"   ⚠️ Fehlende Gruppen: {', '.join(missing_groups)}")
            print(f"   💡 Hinzufügen mit: sudo usermod -a -G {','.join(missing_groups)} {self.user}")
        else:
            print("   ✅ Alle wichtigen Gruppen vorhanden")
        
        print()
    
    def check_usb_device(self):
        """Prüft USB-Device-Status"""
        print("🔌 USB-Device-Status:")
        
        try:
            # lsusb verwenden falls verfügbar
            result = subprocess.run(['lsusb'], capture_output=True, text=True)
            if result.returncode == 0:
                goodix_lines = [line for line in result.stdout.split('\n') 
                               if '27c6' in line.lower() or 'goodix' in line.lower()]
                
                if goodix_lines:
                    print("   ✅ Goodix-Device gefunden:")
                    for line in goodix_lines:
                        print(f"      {line.strip()}")
                else:
                    print("   ❌ Goodix-Device nicht in lsusb gefunden")
            else:
                print("   ⚠️ lsusb nicht verfügbar")
        except FileNotFoundError:
            print("   ⚠️ lsusb-Kommando nicht gefunden")
        
        # USB-Device-Dateien prüfen
        print("\n   USB-Device-Dateien:")
        usb_devices = []
        try:
            for bus_dir in os.listdir('/dev/bus/usb/'):
                bus_path = f'/dev/bus/usb/{bus_dir}'
                if os.path.isdir(bus_path):
                    for device_file in os.listdir(bus_path):
                        device_path = f'{bus_path}/{device_file}'
                        if os.path.isfile(device_path):
                            # Berechtigung prüfen
                            stat = os.stat(device_path)
                            readable = os.access(device_path, os.R_OK)
                            writable = os.access(device_path, os.W_OK)
                            
                            if readable and writable:
                                usb_devices.append(device_path)
        except PermissionError:
            print("      ⚠️ Keine Berechtigung für /dev/bus/usb/")
        except FileNotFoundError:
            print("      ⚠️ /dev/bus/usb/ nicht gefunden")
        
        if usb_devices:
            print(f"      ✅ {len(usb_devices)} USB-Devices mit R/W-Zugriff")
        else:
            print("      ❌ Keine USB-Devices mit ausreichenden Berechtigungen")
        
        print()
    
    def check_udev_rules(self):
        """Prüft udev-Regeln"""
        print("📋 udev-Regeln:")
        
        udev_files = [
            '/etc/udev/rules.d/99-goodix-sensor.rules',
            '/etc/udev/rules.d/99-goodix-fingerprint.rules',
            '/lib/udev/rules.d/60-libfprint2.rules'
        ]
        
        found_rules = []
        for rule_file in udev_files:
            if os.path.exists(rule_file):
                try:
                    with open(rule_file, 'r') as f:
                        content = f.read()
                        if '27c6' in content.lower() or 'goodix' in content.lower():
                            found_rules.append(rule_file)
                            print(f"   ✅ {rule_file}")
                except PermissionError:
                    print(f"   ⚠️ {rule_file} (keine Leseberechtigung)")
        
        if not found_rules:
            print("   ❌ Keine Goodix-spezifischen udev-Regeln gefunden")
            print("   💡 Ausführen: sudo ./fix_usb_permissions.sh")
        
        print()
    
    def test_python_usb_access(self):
        """Testet Python USB-Zugriff"""
        print("🐍 Python USB-Zugriff:")
        
        try:
            import usb.core
            import usb.util
            
            # Suche nach Goodix-Device
            device = usb.core.find(idVendor=0x27C6, idProduct=0x55A2)
            
            if device is None:
                print("   ❌ Goodix-Device nicht über pyusb gefunden")
                print("   💡 Mögliche Ursachen:")
                print("      - Device nicht angeschlossen")
                print("      - USB-Berechtigungen fehlen")
                print("      - Device von anderem Prozess verwendet")
            else:
                print("   ✅ Goodix-Device über pyusb gefunden")
                print(f"      Bus: {device.bus}, Address: {device.address}")
                
                # Versuche grundlegende Informationen abzurufen
                try:
                    print(f"      Vendor ID: 0x{device.idVendor:04X}")
                    print(f"      Product ID: 0x{device.idProduct:04X}")
                    print(f"      Device Class: {device.bDeviceClass}")
                    print("   ✅ Grundlegende Device-Informationen abrufbar")
                except Exception as e:
                    print(f"   ⚠️ Device-Info-Fehler: {e}")
        
        except ImportError:
            print("   ❌ pyusb nicht installiert")
            print("   💡 Installieren mit: pip3 install pyusb")
        except Exception as e:
            print(f"   ❌ USB-Zugriff-Fehler: {e}")
        
        print()
    
    def test_goodix_driver(self):
        """Testet unseren Goodix-Treiber"""
        print("🤖 Goodix-Treiber-Test:")
        
        try:
            driver = GoodixFingerprintDriver()
            
            # Verbindungstest
            if driver.connect():
                print("   ✅ Verbindung erfolgreich")
                
                # Device-Info sammeln
                info = driver.get_device_info()
                for key, value in info.items():
                    if value:
                        print(f"      {key}: {value}")
                
                # Initialisierungs-Test
                if driver.initialize():
                    print("   ✅ Initialisierung erfolgreich")
                else:
                    print("   ⚠️ Initialisierung mit Warnungen (kann normal sein)")
                
                driver.disconnect()
                
            else:
                print("   ❌ Verbindung fehlgeschlagen")
                print("   💡 Überprüfen Sie:")
                print("      - USB-Berechtigungen (sudo ./fix_usb_permissions.sh)")
                print("      - Device-Verbindung")
                print("      - Andere Software, die den Sensor nutzt")
        
        except Exception as e:
            print(f"   ❌ Treiber-Test-Fehler: {e}")
        
        print()
    
    def generate_recommendations(self):
        """Generiert Empfehlungen basierend auf der Diagnose"""
        print("💡 Empfehlungen:")
        
        # Allgemeine Empfehlungen
        recommendations = [
            "1. USB-Berechtigungen einrichten: sudo ./fix_usb_permissions.sh",
            "2. Benutzer aus- und wieder einloggen (für Gruppenmitgliedschaft)",
            "3. USB-Connector ab- und wieder anstecken",
            "4. Ohne sudo testen: ./goodix_login.py test",
            "5. Bei Erfolg: Fingerabdruck registrieren mit ./goodix_login.py enroll"
        ]
        
        for rec in recommendations:
            print(f"   {rec}")
        
        print("\n📞 Bei Problemen:")
        print("   - Detaillierte Logs: export GOODIX_DEBUG=1")
        print("   - Alternative: Protokoll-Analyzer verwenden")
        print("   - Community: Issue in GitHub erstellen")

def main():
    """Hauptfunktion"""
    print("🔍 Goodix Sensor Diagnose")
    print("=" * 30)
    print()
    
    diag = GoodixDiagnostics()
    
    # Diagnose durchführen
    diag.check_user_permissions()
    diag.check_usb_device()
    diag.check_udev_rules()
    diag.test_python_usb_access()
    diag.test_goodix_driver()
    diag.generate_recommendations()
    
    print("\n🏁 Diagnose abgeschlossen!")

if __name__ == "__main__":
    main()
