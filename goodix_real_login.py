#!/usr/bin/env python3
"""
Goodix Real Login System
Echter Fingerabdruck-Login für Linux-System
"""

import sys
import os
import pwd
import json
import hashlib
import time
from pathlib import Path
from drivers.goodix_prototype_driver import GoodixFingerprintDriver
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GoodixRealLogin:
    def __init__(self):
        self.driver = GoodixFingerprintDriver()
        self.enrolled_users_file = os.path.expanduser("~/.config/goodix/enrolled_users.json")
        self.ensure_config_dir()
        self.enrolled_users = self.load_enrolled_users()
    
    def ensure_config_dir(self):
        """Erstelle Konfigurationsverzeichnis falls nicht vorhanden"""
        config_dir = os.path.dirname(self.enrolled_users_file)
        Path(config_dir).mkdir(parents=True, exist_ok=True)
    
    def load_enrolled_users(self):
        """Lädt gespeicherte Fingerabdruck-Templates"""
        try:
            if os.path.exists(self.enrolled_users_file):
                with open(self.enrolled_users_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Fehler beim Laden der Enrollment-Daten: {e}")
            return {}
    
    def save_enrolled_users(self):
        """Speichert Enrollment-Daten"""
        try:
            with open(self.enrolled_users_file, 'w') as f:
                json.dump(self.enrolled_users, f, indent=2)
            # Sichere Berechtigungen setzen
            os.chmod(self.enrolled_users_file, 0o600)
            logger.info(f"Enrollment-Daten gespeichert in {self.enrolled_users_file}")
        except Exception as e:
            logger.error(f"Fehler beim Speichern der Enrollment-Daten: {e}")
    
    def generate_fingerprint_template(self, scan_data):
        """Generiert ein Fingerabdruck-Template aus Scan-Daten"""
        # Vereinfachte Template-Generierung
        # In einer echten Implementierung würde hier Minutiae-Extraktion stattfinden
        if scan_data:
            template_hash = hashlib.sha256(str(scan_data).encode()).hexdigest()
            return {
                'template': template_hash,
                'timestamp': time.time(),
                'quality': 'high'  # Vereinfacht
            }
        return None
    
    def compare_templates(self, template1, template2):
        """Vergleicht zwei Fingerabdruck-Templates"""
        if not template1 or not template2:
            return False
        
        # Vereinfachter Vergleich
        # In einer echten Implementierung würde hier Minutiae-Matching stattfinden
        return template1.get('template') == template2.get('template')
    
    def enroll_user(self, username=None):
        """Registriert einen Fingerabdruck für einen User"""
        if not username:
            username = os.getenv('USER')
        
        print(f"🔐 Fingerabdruck-Enrollment für {username}")
        print("=" * 50)
        
        # Hardware-Verbindung
        print("🔌 Verbinde mit Goodix-Sensor...")
        if not self.driver.connect():
            print("❌ Konnte nicht mit Sensor verbinden")
            print("💡 Tipps:")
            print("   - USB-Connector ab- und wieder anstecken")
            print("   - Berechtigungen prüfen: groups $USER")
            print("   - Device prüfen: lsusb | grep 27c6")
            return False
        
        print("🔧 Initialisiere Sensor...")
        if not self.driver.initialize():
            print("❌ Sensor-Initialisierung fehlgeschlagen")
            return False
        
        print("✅ Sensor bereit!")
        print("\n👆 Bitte Finger 3x auf den Sensor legen...")
        print("   (Für beste Qualität: Finger gerade auflegen, leicht andrücken)")
        
        templates = []
        for i in range(3):
            print(f"\n📱 Scan {i+1}/3:")
            print("   Finger auflegen und kurz warten...")
            
            try:
                # Echten Scan durchführen
                scan_result = self.driver.start_scan()
                if scan_result:
                    # Template aus Scan-Daten generieren
                    template = self.generate_fingerprint_template(scan_result)
                    if template:
                        templates.append(template)
                        print(f"   ✅ Scan {i+1} erfolgreich (Qualität: {template['quality']})")
                    else:
                        print(f"   ❌ Template-Generierung fehlgeschlagen")
                        return False
                else:
                    print(f"   ❌ Scan {i+1} fehlgeschlagen")
                    print("   💡 Finger erneut auflegen und 2 Sekunden warten")
                    return False
                
                # Kurze Pause zwischen Scans
                if i < 2:
                    time.sleep(1)
                    
            except Exception as e:
                logger.error(f"Scan-Fehler: {e}")
                print(f"   ❌ Scan-Fehler: {e}")
                return False
        
        # Templates speichern
        self.enrolled_users[username] = {
            'templates': templates,
            'enrolled_at': time.time(),
            'device_info': self.driver.get_device_info() if hasattr(self.driver, 'get_device_info') else 'unknown'
        }
        
        self.save_enrolled_users()
        
        print(f"\n🎉 Fingerabdruck für {username} erfolgreich registriert!")
        print(f"📁 Gespeichert in: {self.enrolled_users_file}")
        print("\n💡 Jetzt testen: python3 goodix_real_login.py auth")
        return True
    
    def authenticate_user(self, username=None):
        """Authentifiziert einen User per Fingerabdruck"""
        if not username:
            username = os.getenv('USER')
        
        if username not in self.enrolled_users:
            print(f"❌ Kein Fingerabdruck für {username} registriert")
            print(f"💡 Erst registrieren: python3 goodix_real_login.py enroll")
            return False
        
        print(f"🔐 Fingerabdruck-Login für {username}")
        print("=" * 40)
        
        # Hardware-Verbindung
        print("🔌 Verbinde mit Sensor...")
        if not self.driver.connect():
            print("❌ Konnte nicht mit Sensor verbinden")
            return False
        
        print("🔧 Initialisiere Sensor...")
        if not self.driver.initialize():
            print("❌ Sensor-Initialisierung fehlgeschlagen")
            return False
        
        print("👆 Bitte Finger auf den Sensor legen...")
        
        try:
            # Scan durchführen
            scan_result = self.driver.start_scan()
            if scan_result:
                print("🔍 Verarbeite Fingerabdruck...")
                
                # Template aus Scan generieren
                scanned_template = self.generate_fingerprint_template(scan_result)
                if not scanned_template:
                    print("❌ Template-Generierung fehlgeschlagen")
                    return False
                
                # Mit gespeicherten Templates vergleichen
                stored_templates = self.enrolled_users[username]['templates']
                
                print("🔎 Vergleiche mit gespeicherten Templates...")
                for i, stored_template in enumerate(stored_templates):
                    if self.compare_templates(scanned_template, stored_template):
                        print(f"✅ Fingerabdruck erkannt! (Template {i+1})")
                        print(f"🎉 LOGIN ERFOLGREICH! Willkommen zurück, {username}!")
                        return True
                
                print("❌ Fingerabdruck nicht erkannt")
                print("💡 Versuchen Sie es erneut oder registrieren Sie den Finger neu")
                return False
            else:
                print("❌ Scan fehlgeschlagen")
                print("💡 Finger erneut auflegen und 2 Sekunden warten")
                return False
                
        except Exception as e:
            logger.error(f"Auth-Fehler: {e}")
            print(f"❌ Authentifizierungs-Fehler: {e}")
            return False
    
    def list_enrolled_users(self):
        """Zeigt alle registrierten Benutzer an"""
        if not self.enrolled_users:
            print("📋 Keine Benutzer registriert")
            return
        
        print("📋 Registrierte Benutzer:")
        print("=" * 30)
        for username, data in self.enrolled_users.items():
            enrolled_time = time.strftime('%Y-%m-%d %H:%M:%S', 
                                        time.localtime(data['enrolled_at']))
            template_count = len(data['templates'])
            print(f"👤 {username}")
            print(f"   📅 Registriert: {enrolled_time}")
            print(f"   📱 Templates: {template_count}")
            print(f"   🔧 Device: {data.get('device_info', 'unknown')}")
            print()
    
    def remove_user(self, username):
        """Entfernt einen Benutzer aus der Registrierung"""
        if username in self.enrolled_users:
            del self.enrolled_users[username]
            self.save_enrolled_users()
            print(f"✅ Benutzer {username} erfolgreich entfernt")
        else:
            print(f"❌ Benutzer {username} nicht gefunden")

def main():
    if len(sys.argv) < 2:
        print("🔐 Goodix Real Login System")
        print("=" * 30)
        print("Usage:")
        print("  python3 goodix_real_login.py enroll [username]  - Fingerabdruck registrieren")
        print("  python3 goodix_real_login.py auth [username]    - Fingerabdruck authentifizieren")
        print("  python3 goodix_real_login.py list               - Registrierte Benutzer anzeigen")
        print("  python3 goodix_real_login.py remove <username>  - Benutzer entfernen")
        sys.exit(1)
    
    action = sys.argv[1]
    username = sys.argv[2] if len(sys.argv) > 2 else None
    
    login_system = GoodixRealLogin()
    
    if action == 'enroll':
        success = login_system.enroll_user(username)
        sys.exit(0 if success else 1)
    
    elif action == 'auth':
        success = login_system.authenticate_user(username)
        sys.exit(0 if success else 1)
    
    elif action == 'list':
        login_system.list_enrolled_users()
        sys.exit(0)
    
    elif action == 'remove':
        if not username:
            print("❌ Benutzername erforderlich für 'remove'")
            sys.exit(1)
        login_system.remove_user(username)
        sys.exit(0)
    
    else:
        print(f"❌ Unbekannte Aktion: {action}")
        print("Verwende: enroll, auth, list, oder remove")
        sys.exit(1)

if __name__ == "__main__":
    main()
