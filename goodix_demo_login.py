#!/usr/bin/env python3
"""
Goodix Fingerprint Demo-Login
Nutzt Hardware-Erkennung für simulierten Fingerabdruck-Login
"""

import sys
import os
import json
import time
from drivers.goodix_prototype_driver import GoodixFingerprintDriver

class GoodixDemoLogin:
    """Demo-Login mit Hardware-Erkennung"""
    
    def __init__(self):
        self.driver = GoodixFingerprintDriver()
        self.enrolled_users = self.load_enrolled_users()
    
    def load_enrolled_users(self):
        """Lädt registrierte Benutzer"""
        try:
            with open('/tmp/goodix_demo_users.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def save_enrolled_users(self):
        """Speichert registrierte Benutzer"""
        with open('/tmp/goodix_demo_users.json', 'w') as f:
            json.dump(self.enrolled_users, f, indent=2)
    
    def enroll_user(self, username):
        """Registriert einen Benutzer (Hardware-Test)"""
        print(f"🔐 Hardware-Demo-Enrollment für {username}")
        print("=" * 50)
        
        # Hardware-Test
        if not self.driver.connect():
            print("❌ Hardware nicht verfügbar")
            return False
        
        if not self.driver.initialize():
            print("❌ Sensor-Initialisierung fehlgeschlagen") 
            return False
        
        print("✅ Hardware-Verbindung erfolgreich!")
        print("✅ Sensor-Initialisierung erfolgreich!")
        print()
        
        # Demo-Enrollment (simuliert)
        print("📋 Demo-Enrollment-Prozess:")
        print("   (Echte Fingerabdruck-Scans werden simuliert)")
        print()
        
        for i in range(3):
            print(f"👆 Scan {i+1}/3: Drücken Sie Enter zum Fortfahren...")
            input()
            
            # Hardware-Test für jeden "Scan"
            device_info = self.driver.get_device_info()
            if device_info['connected']:
                print(f"   ✅ Scan {i+1} - Hardware reagiert korrekt")
                time.sleep(1)
            else:
                print(f"   ❌ Scan {i+1} - Hardware-Problem")
                return False
        
        # Benutzer speichern
        self.enrolled_users[username] = {
            'enrolled_date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'hardware_verified': True,
            'demo_templates': ['template1', 'template2', 'template3']
        }
        self.save_enrolled_users()
        
        self.driver.disconnect()
        
        print()
        print(f"🎉 Demo-Enrollment für {username} erfolgreich!")
        print("   Hardware-Kommunikation funktioniert perfekt")
        print("   Fingerabdruck-Templates simuliert und gespeichert")
        
        return True
    
    def authenticate_user(self, username):
        """Authentifiziert Benutzer (Hardware-Test)"""
        print(f"🔐 Hardware-Demo-Login für {username}")
        print("=" * 40)
        
        if username not in self.enrolled_users:
            print(f"❌ {username} ist nicht registriert")
            print("   Bitte zuerst: ./goodix_demo_login.py enroll")
            return False
        
        # Hardware-Test
        if not self.driver.connect():
            print("❌ Hardware nicht verfügbar")
            return False
        
        if not self.driver.initialize():
            print("❌ Sensor-Initialisierung fehlgeschlagen")
            return False
        
        print("✅ Hardware-Verbindung erfolgreich!")
        print("✅ Sensor-Initialisierung erfolgreich!")
        print()
        
        # Demo-Authentifizierung
        print("👆 Demo-Fingerabdruck-Scan:")
        print("   Drücken Sie Enter für 'Finger auflegen'...")
        input()
        
        # Hardware reagiert
        device_info = self.driver.get_device_info()
        if device_info['connected']:
            print("   📡 Hardware-Sensor reagiert...")
            time.sleep(1)
            print("   🔍 Template-Vergleich (simuliert)...")
            time.sleep(1)
            print("   ✅ Fingerabdruck erkannt!")
            
            self.driver.disconnect()
            
            print()
            print("🎉 LOGIN ERFOLGREICH!")
            print(f"   Willkommen zurück, {username}!")
            print(f"   Letzte Registrierung: {self.enrolled_users[username]['enrolled_date']}")
            
            return True
        else:
            print("   ❌ Hardware-Problem")
            self.driver.disconnect()
            return False

def main():
    if len(sys.argv) < 2:
        print("🔐 Goodix Demo-Login")
        print()
        print("Verwendung:")
        print("  ./goodix_demo_login.py enroll [benutzer]    - Benutzer registrieren")
        print("  ./goodix_demo_login.py auth [benutzer]      - Benutzer anmelden")
        print("  ./goodix_demo_login.py list                 - Registrierte Benutzer")
        sys.exit(1)
    
    action = sys.argv[1]
    username = sys.argv[2] if len(sys.argv) > 2 else os.getenv('USER')
    
    login = GoodixDemoLogin()
    
    if action == 'enroll':
        success = login.enroll_user(username)
        sys.exit(0 if success else 1)
    
    elif action == 'auth':
        success = login.authenticate_user(username) 
        sys.exit(0 if success else 1)
    
    elif action == 'list':
        print("📋 Registrierte Demo-Benutzer:")
        if login.enrolled_users:
            for user, data in login.enrolled_users.items():
                print(f"   👤 {user} - {data['enrolled_date']}")
        else:
            print("   (Keine Benutzer registriert)")
        sys.exit(0)
    
    else:
        print(f"❌ Unbekannte Aktion: {action}")
        sys.exit(1)

if __name__ == "__main__":
    main()
