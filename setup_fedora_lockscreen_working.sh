#!/bin/bash
# 🔐 Goodix Lockscreen Integration für Fedora/GNOME
# Nutzt unser funktionierendes Ultra-Simple System

echo "🔐 Goodix Lockscreen Integration Setup"
echo "====================================="

# 1. Erstelle Unlock-Script
echo "📝 Erstelle Unlock-Script..."
mkdir -p ~/.local/bin

cat > ~/.local/bin/goodix-unlock << 'EOF'
#!/bin/bash
# Goodix Unlock für GNOME Lockscreen

# Prüfe ob Bildschirm gesperrt ist
if pgrep gnome-screensaver > /dev/null || pgrep gnome-session-binary > /dev/null; then
    # Zeige Notification
    notify-send "🔐 Goodix Unlock" "Drücke ENTER für Fingerabdruck-Scan..." -t 5000 &
    
    # Terminal für Fingerabdruck-Auth öffnen
    gnome-terminal --title="Goodix Unlock" --geometry=60x15+100+100 -- bash -c "
        cd /home/mikail/goodix-fingerprint-linux
        echo '🔐 Goodix Fingerabdruck-Unlock'
        echo '=============================='
        echo 'Führe Authentifizierung durch...'
        echo ''
        
        if python3 goodix_ultra_simple.py auth; then
            echo ''
            echo '✅ Authentifizierung erfolgreich!'
            echo 'Entsperre Bildschirm...'
            
            # GNOME entsperren
            dbus-send --session --dest=org.gnome.ScreenSaver --type=method_call /org/gnome/ScreenSaver org.gnome.ScreenSaver.SetActive boolean:false 2>/dev/null
            
            # Alternative Unlock-Methoden
            gnome-screensaver-command --deactivate 2>/dev/null
            loginctl unlock-session 2>/dev/null
            
            notify-send '✅ Unlock erfolgreich' 'Willkommen zurück!' -t 3000
            sleep 2
        else
            echo ''
            echo '❌ Authentifizierung fehlgeschlagen!'
            notify-send '❌ Unlock fehlgeschlagen' 'Fingerabdruck nicht erkannt' -t 3000
            echo 'Drücke ENTER zum Schließen...'
            read
        fi
    "
else
    notify-send "ℹ️ Goodix Info" "Bildschirm ist nicht gesperrt" -t 2000
fi
EOF

chmod +x ~/.local/bin/goodix-unlock

# 2. Desktop-Eintrag für Anwendungen erstellen
echo "🖥️ Erstelle Desktop-Integration..."
mkdir -p ~/.local/share/applications

cat > ~/.local/share/applications/goodix-unlock.desktop << EOF
[Desktop Entry]
Name=Goodix Fingerprint Unlock
Comment=Entsperre Bildschirm mit Fingerabdruck
Exec=/home/mikail/.local/bin/goodix-unlock
Icon=fingerprint
Terminal=false
Type=Application
Categories=System;Security;
EOF

cat > ~/.local/share/applications/goodix-enroll.desktop << EOF
[Desktop Entry]
Name=Goodix Fingerprint Enrollment
Comment=Fingerabdruck registrieren
Exec=gnome-terminal -- bash -c "cd /home/mikail/goodix-fingerprint-linux && python3 goodix_ultra_simple.py enroll && read -p 'Drücke ENTER zum Schließen...'"
Icon=fingerprint
Terminal=false
Type=Application
Categories=System;Security;
EOF

# 3. GNOME-Tastenkombination konfigurieren
echo "⌨️ Erstelle Tastenkombination-Script..."
cat > ~/.local/bin/setup-goodix-hotkey << 'EOF'
#!/bin/bash
# Setup für Goodix Tastenkombination

echo "⌨️ Richte Goodix-Tastenkombination ein (Super+F)..."

# GNOME-Settings öffnen und Anleitung zeigen
gnome-control-center keyboard &

echo ""
echo "📋 MANUELLE SCHRITTE (GNOME-Einstellungen):"
echo "==========================================="
echo "1. Gehe zu: Tastatur → Tastenkombinationen anzeigen und anpassen"
echo "2. Scrolle nach unten zu 'Benutzerdefinierte Tastenkombinationen'"
echo "3. Klicke '+' für neue Tastenkombination"
echo "4. Name: Goodix Fingerprint Unlock"
echo "5. Befehl: /home/mikail/.local/bin/goodix-unlock"
echo "6. Tastenkombination: Super+F (oder deine Wahl)"
echo "7. Fertig!"
echo ""
echo "🎯 Danach: Super+F drücken für Fingerabdruck-Unlock!"

EOF
chmod +x ~/.local/bin/setup-goodix-hotkey

# 4. Auto-Unlock Script für Login-Screen (optional)
echo "🚪 Erstelle Login-Screen Integration..."
cat > ~/.local/bin/goodix-login-helper << 'EOF'
#!/bin/bash
# Goodix Helper für Login-Screen

cd /home/mikail/goodix-fingerprint-linux

echo "🔐 Goodix Login-Helper"
echo "Teste Fingerabdruck-Authentifizierung..."

if python3 goodix_ultra_simple.py auth; then
    echo "✅ Fingerabdruck erkannt - Login erfolgreich!"
    exit 0
else
    echo "❌ Fingerabdruck nicht erkannt"
    exit 1
fi
EOF
chmod +x ~/.local/bin/goodix-login-helper

# 5. Systemd-Service für automatischen Start (optional)
echo "🔄 Erstelle Systemd-Service..."
mkdir -p ~/.config/systemd/user

cat > ~/.config/systemd/user/goodix-monitor.service << EOF
[Unit]
Description=Goodix Fingerprint Monitor
After=graphical-session.target

[Service]
Type=simple
ExecStart=/home/mikail/.local/bin/goodix-unlock
Restart=on-failure
Environment=DISPLAY=:0

[Install]
WantedBy=default.target
EOF

# Services aktivieren (optional)
# systemctl --user enable goodix-monitor.service

echo ""
echo "✅ Goodix Lockscreen Integration installiert!"
echo ""
echo "📋 Verfügbare Funktionen:"
echo "========================"
echo "1. 🖥️ Desktop-Apps:"
echo "   - Goodix Fingerprint Unlock (in Anwendungen)"
echo "   - Goodix Fingerprint Enrollment (in Anwendungen)"
echo ""
echo "2. 🔧 Terminal-Befehle:"
echo "   - goodix-unlock                 (Unlock-Script)"
echo "   - setup-goodix-hotkey          (Tastenkombination einrichten)"
echo "   - goodix-login-helper          (Login-Helper)"
echo ""
echo "3. ⌨️ Tastenkombination einrichten:"
echo "   setup-goodix-hotkey"
echo ""
echo "4. 🧪 System testen:"
echo "   - Bildschirm sperren: Super+L"
echo "   - Goodix-Unlock verwenden"
echo ""
echo "💡 NÄCHSTE SCHRITTE:"
echo "==================="
echo "1. Tastenkombination einrichten: setup-goodix-hotkey"
echo "2. Bildschirm sperren und testen: Super+L"
echo "3. Goodix-Unlock verwenden: Super+F (nach Setup)"
echo ""
echo "🎉 Dein Goodix-Sensor ist bereit für Fedora-Lockscreen!"
