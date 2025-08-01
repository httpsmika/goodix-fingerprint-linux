#!/usr/bin/env python3
"""
Goodix Fingerprint Login Manager
Praktische Anwendung für Fingerabdruck-basierte Authentifizierung
"""

import sys
import os
import json
import time
import hashlib
import getpass
from pathlib import Path
from drivers.goodix_prototype_driver import GoodixFingerprintDriver
import logging

class GoodixLoginManager:
    """Verwaltet Fingerabdruck-Login für Goodix-Sensor"""
    
    def __init__(self):
        self.driver = GoodixFingerprintDriver()
        self.data_file = Path.home() / '.goodix_fingerprints.json'
        self.enrolled_users = self.load_enrollment_data()
        
        # Logging konfigurieren
        logging.basicConfig(level=logging.INFO,
                          format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
    
    def load_enrollment_data(self) -> dict:
        """Lädt gespeicherte Fingerabdruck-Daten"""
        try:
            if self.data_file.exists():
                with open(self.data_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.warning(f"Konnte Enrollment-Daten nicht laden: {e}")
        
        return {}
    
    def save_enrollment_data(self):
        """Speichert Fingerabdruck-Daten"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.enrolled_users, f, indent=2)
            
            # Datei-Berechtigung auf User beschränken
            os.chmod(self.data_file, 0o600)
            
        except Exception as e:
            self.logger.error(f"Konnte Enrollment-Daten nicht speichern: {e}")
    
    def generate_fingerprint_template(self, scan_data: bytes) -> str:
        """Generiert ein Fingerabdruck-Template aus Scan-Daten"""
        # Vereinfachtes Template-System für Demo
        # In einem echten System würden hier komplexe biometrische
        # Algorithmen verwendet werden
        
        if not scan_data or len(scan_data) == 0:
            return None
        
        # Hash der Scan-Daten als einfaches "Template"
        template_hash = hashlib.sha256(scan_data).hexdigest()
        
        # Zusätzliche Metadaten
        template = {
            'hash': template_hash,
            'timestamp': time.time(),
            'length': len(scan_data),
            'quality': self.assess_scan_quality(scan_data)
        }
        
        return json.dumps(template)
    
    def assess_scan_quality(self, scan_data: bytes) -> str:
        """Bewertet die Qualität eines Fingerabdruck-Scans"""
        if not scan_data:
            return 'poor'
        
        # Einfache Qualitätsbewertung basierend auf Daten-Eigenschaften
        if len(scan_data) < 100:
            return 'poor'
        elif len(scan_data) < 500:
            return 'fair'
        else:
            return 'good'
    
    def enroll_fingerprint(self, username: str = None) -> bool:
        """Registriert einen neuen Fingerabdruck"""
        if username is None:
            username = getpass.getuser()
        
        print(f"🔐 Fingerabdruck-Registrierung für Benutzer: {username}")
        print("=" * 50)
        
        # Mit Sensor verbinden
        if not self.driver.connect():
            print("❌ Fehler: Konnte nicht mit Goodix-Sensor verbinden")
            print("   Überprüfen Sie:")
            print("   - USB-Verbindung")
            print("   - Berechtigung (evtl. sudo erforderlich)")
            print("   - Device-Status mit: python3 tools/device_scanner.py")
            return False
        
        try:
            # Sensor initialisieren
            if not self.driver.initialize():
                print("❌ Fehler: Sensor-Initialisierung fehlgeschlagen")
                return False
            
            print("✅ Sensor bereit!")
            print("\n📋 Registrierungsprozess:")
            print("   Legen Sie Ihren Finger 3x auf den Sensor")
            print("   für eine zuverlässige Registrierung\n")
            
            templates = []
            
            for scan_num in range(3):
                print(f"👆 Scan {scan_num + 1}/3: Finger auf Sensor legen...")
                
                # Callback für Scan-Events
                scan_completed = False
                scan_data = None
                
                def on_scan_complete(image_data):
                    nonlocal scan_completed, scan_data
                    scan_completed = True
                    scan_data = image_data
                
                self.driver.on_scan_complete = on_scan_complete
                
                # Scan starten
                if self.driver.start_scan():
                    # Warten auf Scan-Completion
                    timeout = 30  # 30 Sekunden Timeout
                    start_time = time.time()
                    
                    while not scan_completed and (time.time() - start_time) < timeout:
                        time.sleep(0.1)
                    
                    if scan_completed and scan_data:
                        template = self.generate_fingerprint_template(scan_data)
                        if template:
                            templates.append(template)
                            print(f"   ✅ Scan {scan_num + 1} erfolgreich!")
                        else:
                            print(f"   ❌ Scan {scan_num + 1} - Template-Erstellung fehlgeschlagen")
                            return False
                    else:
                        print(f"   ⏱️ Scan {scan_num + 1} - Timeout oder kein Finger erkannt")
                        return False
                else:
                    print(f"   ❌ Scan {scan_num + 1} - Scan-Start fehlgeschlagen")
                    return False
                
                # Kurze Pause zwischen Scans
                if scan_num < 2:
                    print("   Finger entfernen und kurz warten...")
                    time.sleep(2)
            
            # Templates speichern
            self.enrolled_users[username] = {
                'templates': templates,
                'enrolled_at': time.time(),
                'scan_count': len(templates)
            }
            
            self.save_enrollment_data()
            
            print(f"\n🎉 Fingerabdruck für '{username}' erfolgreich registriert!")
            print(f"📊 {len(templates)} Templates gespeichert")
            return True
            
        except KeyboardInterrupt:
            print("\n\n❌ Registrierung abgebrochen")
            return False
        finally:
            self.driver.disconnect()
    
    def authenticate_user(self, username: str = None) -> bool:
        """Authentifiziert einen Benutzer per Fingerabdruck"""
        if username is None:
            username = getpass.getuser()
        
        # Prüfen ob User registriert ist
        if username not in self.enrolled_users:
            print(f"❌ Kein Fingerabdruck für Benutzer '{username}' registriert")
            print(f"   Registrierung mit: {sys.argv[0]} enroll")
            return False
        
        print(f"🔐 Fingerabdruck-Login für: {username}")
        print("👆 Bitte Finger auf den Sensor legen...")
        
        # Mit Sensor verbinden
        if not self.driver.connect():
            print("❌ Fehler: Konnte nicht mit Sensor verbinden")
            return False
        
        try:
            # Sensor initialisieren
            if not self.driver.initialize():
                print("❌ Fehler: Sensor-Initialisierung fehlgeschlagen")
                return False
            
            # Auth-Scan durchführen
            scan_completed = False
            scan_data = None
            
            def on_scan_complete(image_data):
                nonlocal scan_completed, scan_data
                scan_completed = True
                scan_data = image_data
            
            self.driver.on_scan_complete = on_scan_complete
            
            if self.driver.start_scan():
                # Warten auf Scan
                timeout = 15  # 15 Sekunden für Auth
                start_time = time.time()
                
                while not scan_completed and (time.time() - start_time) < timeout:
                    time.sleep(0.1)
                
                if scan_completed and scan_data:
                    # Template generieren und vergleichen
                    auth_template = self.generate_fingerprint_template(scan_data)
                    
                    if self.match_template(auth_template, username):
                        print("✅ Fingerabdruck-Authentifizierung erfolgreich!")
                        return True
                    else:
                        print("❌ Fingerabdruck nicht erkannt")
                        return False
                else:
                    print("⏱️ Timeout - kein Finger erkannt")
                    return False
            else:
                print("❌ Scan-Start fehlgeschlagen")
                return False
                
        except KeyboardInterrupt:
            print("\n❌ Authentifizierung abgebrochen")
            return False
        finally:
            self.driver.disconnect()
    
    def match_template(self, auth_template: str, username: str) -> bool:
        """Vergleicht Auth-Template mit gespeicherten Templates"""
        if not auth_template:
            return False
        
        try:
            auth_data = json.loads(auth_template)
            stored_templates = self.enrolled_users[username]['templates']
            
            # Vereinfachter Matching-Algorithmus
            # In einem echten System würden hier biometrische
            # Matching-Algorithmen verwendet werden
            
            for stored_template_str in stored_templates:
                stored_data = json.loads(stored_template_str)
                
                # Hash-Vergleich als einfacher Matcher
                if auth_data['hash'] == stored_data['hash']:
                    return True
                
                # Zusätzlich: Ähnlichkeits-Check könnte hier implementiert werden
            
            return False
            
        except Exception as e:
            self.logger.error(f"Template-Matching-Fehler: {e}")
            return False
    
    def list_enrolled_users(self):
        """Zeigt registrierte Benutzer an"""
        if not self.enrolled_users:
            print("📋 Keine Benutzer registriert")
            return
        
        print("📋 Registrierte Benutzer:")
        print("=" * 30)
        
        for username, data in self.enrolled_users.items():
            enrolled_time = time.strftime('%Y-%m-%d %H:%M:%S', 
                                        time.localtime(data['enrolled_at']))
            print(f"👤 {username}")
            print(f"   📅 Registriert: {enrolled_time}")
            print(f"   📊 Templates: {data['scan_count']}")
            print()
    
    def remove_user(self, username: str):
        """Entfernt einen registrierten Benutzer"""
        if username in self.enrolled_users:
            del self.enrolled_users[username]
            self.save_enrollment_data()
            print(f"✅ Benutzer '{username}' entfernt")
        else:
            print(f"❌ Benutzer '{username}' nicht gefunden")

def main():
    """Hauptfunktion - Command-Line-Interface"""
    
    if len(sys.argv) < 2:
        print("🔐 Goodix Fingerprint Login Manager")
        print("=" * 40)
        print("Verwendung:")
        print(f"  {sys.argv[0]} enroll [username]  - Fingerabdruck registrieren")
        print(f"  {sys.argv[0]} auth [username]    - Authentifizierung durchführen")
        print(f"  {sys.argv[0]} list               - Registrierte Benutzer anzeigen")
        print(f"  {sys.argv[0]} remove <username>  - Benutzer entfernen")
        print(f"  {sys.argv[0]} test               - Sensor-Test")
        print()
        print("Beispiele:")
        print(f"  {sys.argv[0]} enroll            # Aktueller Benutzer")
        print(f"  {sys.argv[0]} auth              # Aktueller Benutzer")
        print(f"  {sys.argv[0]} enroll alice      # Benutzer 'alice'")
        sys.exit(1)
    
    action = sys.argv[1].lower()
    username = sys.argv[2] if len(sys.argv) > 2 else None
    
    manager = GoodixLoginManager()
    
    try:
        if action == 'enroll':
            success = manager.enroll_fingerprint(username)
            sys.exit(0 if success else 1)
        
        elif action == 'auth':
            success = manager.authenticate_user(username)
            sys.exit(0 if success else 1)
        
        elif action == 'list':
            manager.list_enrolled_users()
            sys.exit(0)
        
        elif action == 'remove':
            if not username:
                print("❌ Benutzername erforderlich für 'remove'")
                sys.exit(1)
            manager.remove_user(username)
            sys.exit(0)
        
        elif action == 'test':
            # Sensor-Test
            print("🔧 Goodix-Sensor-Test")
            driver = GoodixFingerprintDriver()
            
            if driver.connect():
                print("✅ Sensor-Verbindung erfolgreich")
                info = driver.get_device_info()
                print("📊 Device-Informationen:")
                for key, value in info.items():
                    print(f"   {key}: {value}")
                driver.disconnect()
                sys.exit(0)
            else:
                print("❌ Sensor-Verbindung fehlgeschlagen")
                sys.exit(1)
        
        else:
            print(f"❌ Unbekannte Aktion: {action}")
            print("Verfügbare Aktionen: enroll, auth, list, remove, test")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\n👋 Abgebrochen")
        sys.exit(1)

if __name__ == "__main__":
    main()
