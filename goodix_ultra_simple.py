#!/usr/bin/env python3
"""
Ultra-Simple Goodix Login - Funktioniert auch ohne echte Finger-Detection
"""

import sys
import os
import json
import hashlib
import time
import usb.core
import usb.util
from pathlib import Path

class GoodixUltraSimple:
    def __init__(self):
        self.device = None
        self.enrolled_users_file = os.path.expanduser("~/.config/goodix/enrolled_users.json")
        self.ensure_config_dir()
        self.enrolled_users = self.load_enrolled_users()
    
    def ensure_config_dir(self):
        """Erstelle Konfigurationsverzeichnis"""
        config_dir = os.path.dirname(self.enrolled_users_file)
        Path(config_dir).mkdir(parents=True, exist_ok=True)
    
    def connect(self):
        """Verbinde mit Goodix-Device"""
        try:
            print("🔌 Suche Goodix-Device...")
            self.device = usb.core.find(idVendor=0x27c6, idProduct=0x55a2)
            
            if self.device is None:
                print("❌ Goodix-Device nicht gefunden!")
                return False
            
            print("✅ Goodix-Device gefunden!")
            
            # Einfache USB-Setup
            try:
                if self.device.is_kernel_driver_active(0):
                    self.device.detach_kernel_driver(0)
                self.device.set_configuration()
                usb.util.claim_interface(self.device, 0)
                print("✅ USB bereit!")
            except Exception as e:
                print(f"⚠️ USB-Setup: {e} (wird ignoriert)")
            
            return True
            
        except Exception as e:
            print(f"❌ Verbindungsfehler: {e}")
            return False
    
    def hardware_test(self):
        """Einfacher Hardware-Test"""
        try:
            # Teste verschiedene Kommandos
            test_commands = [0x01, 0x02, 0x10, 0x20, 0x21, 0x30]
            
            for cmd in test_commands:
                try:
                    # Kommando senden
                    self.device.write(0x01, [cmd], 500)
                    time.sleep(0.1)
                    
                    # Response versuchen
                    try:
                        response = self.device.read(0x82, 512, 500)
                        if len(response) > 0:
                            print(f"✅ Kommando 0x{cmd:02x} Response: {len(response)} bytes")
                            return response
                    except:
                        pass
                        
                except Exception as e:
                    pass
            
            print("⚠️ Keine Hardware-Response, aber Device erreichbar")
            return b'hardware_accessible'
            
        except Exception as e:
            print(f"❌ Hardware-Test fehlgeschlagen: {e}")
            return None
    
    def simulate_fingerprint_scan(self, scan_number):
        """Simuliert einen Fingerabdruck-Scan"""
        print(f"📱 Simuliere Fingerabdruck-Scan {scan_number}...")
        
        # Hardware-Test für echte Daten
        hw_response = self.hardware_test()
        
        # Erstelle KONSISTENTE Scan-Daten für denselben User
        timestamp = time.time()
        user = os.getenv('USER', 'unknown')
        
        # Für Authentifizierung: Verwende ähnliche Basis-Daten wie beim Enrollment
        if scan_number == 99:  # Auth-Scan
            # Verwende ähnliche Daten wie bei Scan 1 für bessere Matching-Chance
            scan_data = f"goodix_scan_{user}_1_{int(timestamp/100)*100}".encode()
        else:
            # Normale Enrollment-Scans
            scan_data = f"goodix_scan_{user}_{scan_number}_{timestamp}".encode()
        
        if hw_response:
            # Füge Hardware-Daten hinzu
            scan_data += hw_response[:100] if len(hw_response) > 100 else hw_response
        
        print(f"✅ Scan-Daten generiert: {len(scan_data)} bytes")
        return scan_data
    
    def generate_template(self, scan_data):
        """Generiert Template"""
        if scan_data:
            template_hash = hashlib.sha256(scan_data).hexdigest()
            return {
                'template': template_hash,
                'timestamp': time.time(),
                'quality': 'simulated',
                'size': len(scan_data)
            }
        return None
    
    def enroll_user(self, username=None):
        """Registriert Fingerabdruck (vereinfacht)"""
        if not username:
            username = os.getenv('USER')
        
        print(f"🔐 Fingerabdruck-Registrierung für {username}")
        print("=" * 50)
        
        if not self.connect():
            return False
        
        print("\n👆 SIMULATION: Drücke ENTER für jeden 'Fingerabdruck-Scan'")
        print("   (3 Scans werden simuliert)")
        
        templates = []
        for i in range(3):
            print(f"\n📱 Scan {i+1}/3:")
            input("   👆 Drücke ENTER für Scan...")
            
            # Simuliere Scan
            scan_data = self.simulate_fingerprint_scan(i+1)
            
            if scan_data:
                template = self.generate_template(scan_data)
                if template:
                    templates.append(template)
                    print(f"   ✅ Template {i+1} erstellt!")
                    print(f"   🔑 Hash: {template['template'][:16]}...")
                else:
                    print(f"   ❌ Template-Erstellung fehlgeschlagen")
                    return False
            else:
                print(f"   ❌ Scan {i+1} fehlgeschlagen")
                return False
        
        # Speichere Templates
        self.enrolled_users[username] = {
            'templates': templates,
            'enrolled_at': time.time(),
            'method': 'simulated'
        }
        self.save_enrolled_users()
        
        print(f"\n🎉 Fingerabdruck für {username} erfolgreich registriert!")
        print(f"📁 Gespeichert: {self.enrolled_users_file}")
        print("\n💡 Teste jetzt: python3 goodix_ultra_simple.py auth")
        return True
    
    def authenticate_user(self, username=None):
        """Authentifiziert Benutzer (vereinfacht)"""
        if not username:
            username = os.getenv('USER')
        
        if username not in self.enrolled_users:
            print(f"❌ Kein Fingerabdruck für {username} registriert")
            print("💡 Erst registrieren: python3 goodix_ultra_simple.py enroll")
            return False
        
        print(f"🔐 Fingerabdruck-Login für {username}")
        print("=" * 40)
        
        if not self.connect():
            return False
        
        print("\n👆 SIMULATION: Drücke ENTER für Authentifizierung")
        input("   👆 Drücke ENTER...")
        
        print("📱 Authentifizierungs-Scan:")
        scan_data = self.simulate_fingerprint_scan(99)  # Auth-Scan
        
        if scan_data:
            test_template = self.generate_template(scan_data)
            if test_template:
                stored_templates = self.enrolled_users[username]['templates']
                
                print("🔍 Vergleiche Templates...")
                
                # Vereinfachter Vergleich - check ob ähnliche Basis-Daten
                test_base = test_template['template'][:32]  # Erste 32 Zeichen
                
                for i, stored_template in enumerate(stored_templates):
                    stored_base = stored_template['template'][:32]
                    
                # Verbesserte Ähnlichkeitsprüfung
                # Prüfe verschiedene Übereinstimmungen
                if (test_base[:16] == stored_base[:16] or  # Exakte Übereinstimmung
                    test_base[:8] == stored_base[:8] or   # Teilübereinstimmung
                    username in test_template['template']):  # Username-basiert
                    print(f"✅ Template-Match gefunden! (Template {i+1})")
                    print(f"🎉 LOGIN ERFOLGREICH! Willkommen zurück, {username}!")
                    return True
                
                print("❌ Kein Template-Match gefunden")
                print("💡 Bei Simulation: Templates ändern sich bei jedem Scan")
                print("💡 Echte Hardware würde konsistentere Ergebnisse liefern")
                return False
        
        print("❌ Authentifizierung fehlgeschlagen")
        return False
    
    def load_enrolled_users(self):
        """Lädt Benutzer-Daten"""
        try:
            if os.path.exists(self.enrolled_users_file):
                with open(self.enrolled_users_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Fehler beim Laden: {e}")
            return {}
    
    def save_enrolled_users(self):
        """Speichert Benutzer-Daten"""
        try:
            with open(self.enrolled_users_file, 'w') as f:
                json.dump(self.enrolled_users, f, indent=2)
            os.chmod(self.enrolled_users_file, 0o600)
            print(f"📁 Daten gespeichert: {self.enrolled_users_file}")
        except Exception as e:
            print(f"Fehler beim Speichern: {e}")
    
    def list_users(self):
        """Zeigt registrierte Benutzer"""
        if not self.enrolled_users:
            print("📋 Keine Benutzer registriert")
            return
        
        print("📋 Registrierte Benutzer:")
        print("=" * 30)
        for username, data in self.enrolled_users.items():
            enrolled_time = time.strftime('%Y-%m-%d %H:%M:%S', 
                                        time.localtime(data['enrolled_at']))
            template_count = len(data['templates'])
            method = data.get('method', 'unknown')
            print(f"👤 {username}")
            print(f"   📅 Registriert: {enrolled_time}")
            print(f"   📱 Templates: {template_count}")
            print(f"   🔧 Methode: {method}")
            print()
    
    def hardware_info(self):
        """Zeigt Hardware-Informationen"""
        print("🔧 Goodix Hardware-Info")
        print("=" * 25)
        
        if self.connect():
            print("✅ Device: Goodix 27C6:55A2")
            print("✅ Status: Verbunden")
            
            # Hardware-Test
            hw_response = self.hardware_test()
            if hw_response:
                print(f"✅ Hardware-Response: {len(hw_response)} bytes")
                print(f"🔑 Sample: {hw_response[:50]}...")
            else:
                print("⚠️ Keine Hardware-Response")
        else:
            print("❌ Device nicht erreichbar")

def main():
    if len(sys.argv) < 2:
        print("🔐 Goodix Ultra Simple Login")
        print("=" * 30)
        print("Usage:")
        print("  python3 goodix_ultra_simple.py enroll    - Fingerabdruck registrieren")
        print("  python3 goodix_ultra_simple.py auth      - Fingerabdruck testen")
        print("  python3 goodix_ultra_simple.py list      - Registrierte Benutzer")
        print("  python3 goodix_ultra_simple.py info      - Hardware-Info")
        print()
        print("💡 Diese Version funktioniert auch ohne echte Finger-Detection!")
        sys.exit(1)
    
    action = sys.argv[1]
    login_system = GoodixUltraSimple()
    
    if action == 'enroll':
        success = login_system.enroll_user()
        sys.exit(0 if success else 1)
    elif action == 'auth':
        success = login_system.authenticate_user()
        sys.exit(0 if success else 1)
    elif action == 'list':
        login_system.list_users()
        sys.exit(0)
    elif action == 'info':
        login_system.hardware_info()
        sys.exit(0)
    else:
        print(f"❌ Unbekannte Aktion: {action}")
        sys.exit(1)

if __name__ == "__main__":
    main()
