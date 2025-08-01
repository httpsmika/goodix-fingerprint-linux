#!/bin/bash
# 🔐 Goodix Fingerprint Setup für Fedora
# Optimiert für dein System

echo "🔐 Goodix Fingerprint Setup für Fedora"
echo "======================================"

# 1. USB-Berechtigungen für Fedora korrekt setzen
echo "📋 Setze USB-Berechtigungen für Fedora..."
echo 'SUBSYSTEM=="usb", ATTRS{idVendor}=="27c6", ATTRS{idProduct}=="55a2", MODE="0666", GROUP="wheel"' | sudo tee /etc/udev/rules.d/99-goodix-fedora.rules

# 2. Benutzer zu wheel-Gruppe hinzufügen (falls noch nicht)
echo "👤 Prüfe wheel-Gruppenmitgliedschaft..."
sudo usermod -a -G wheel $USER

# 3. udev-Regeln neu laden
echo "🔄 Lade udev-Regeln neu..."
sudo udevadm control --reload-rules
sudo udevadm trigger

# 4. Python-Dependencies prüfen
echo "🐍 Prüfe Python-Dependencies..."
pip3 install --user pyusb numpy pillow

# 5. Erstelle lokales bin-Verzeichnis
echo "📁 Erstelle lokales bin-Verzeichnis..."
mkdir -p ~/.local/bin

# 6. Kopiere Goodix-Login-Script
echo "📋 Installiere Goodix-Login-Script..."
cp goodix_login.py ~/.local/bin/
chmod +x ~/.local/bin/goodix_login.py

# 7. PATH erweitern (falls nötig)
if ! echo $PATH | grep -q "$HOME/.local/bin"; then
    echo "🔧 Erweitere PATH..."
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
    echo "✅ PATH wurde erweitert - bitte Terminal neu starten"
fi

# 8. Desktop-Verknüpfung erstellen
echo "🖥️ Erstelle Desktop-Integration..."
mkdir -p ~/.local/share/applications

cat > ~/.local/share/applications/goodix-enroll.desktop << EOF
[Desktop Entry]
Name=Goodix Fingerprint Enrollment
Comment=Fingerabdruck registrieren
Exec=gnome-terminal -- bash -c "cd $PWD && python3 goodix_demo_login.py enroll && read -p 'Drücke Enter zum Schließen...'"
Icon=fingerprint
Terminal=false
Type=Application
Categories=System;Security;
EOF

cat > ~/.local/share/applications/goodix-test.desktop << EOF
[Desktop Entry]
Name=Goodix Fingerprint Test
Comment=Fingerabdruck testen
Exec=gnome-terminal -- bash -c "cd $PWD && python3 goodix_demo_login.py auth && read -p 'Drücke Enter zum Schließen...'"
Icon=fingerprint
Terminal=false
Type=Application
Categories=System;Security;
EOF

# 9. GNOME-Tastenkombination für Unlock erstellen
echo "⌨️ Erstelle Tastenkombination..."
mkdir -p ~/.config/goodix

cat > ~/.config/goodix/goodix_unlock.sh << 'EOF'
#!/bin/bash
# Goodix Unlock Script für GNOME

# Prüfe ob Bildschirm gesperrt ist
if gnome-screensaver-command -q | grep -q "is active"; then
    # Zeige Notification
    notify-send "🔐 Goodix Unlock" "Finger auf Sensor legen..." -t 3000
    
    # Führe Fingerabdruck-Authentifizierung durch
    cd /home/mikail/Fingerabdrucksensor
    if python3 goodix_demo_login.py auth; then
        # Entsperre Bildschirm
        gnome-screensaver-command --deactivate
        notify-send "✅ Unlock erfolgreich" "Willkommen zurück!" -t 2000
    else
        notify-send "❌ Unlock fehlgeschlagen" "Fingerabdruck nicht erkannt" -t 3000
    fi
else
    notify-send "ℹ️ Goodix Info" "Bildschirm ist nicht gesperrt" -t 2000
fi
EOF

chmod +x ~/.config/goodix/goodix_unlock.sh

# 10. Informationen anzeigen
echo ""
echo "✅ Setup abgeschlossen!"
echo ""
echo "📋 Nächste Schritte:"
echo "1. 🔌 USB-Connector ab- und wieder anstecken"
echo "2. 🚪 Terminal neu starten oder neu einloggen"
echo "3. 📱 Fingerabdruck registrieren:"
echo "   python3 goodix_demo_login.py enroll"
echo "4. 🧪 Fingerabdruck testen:"
echo "   python3 goodix_demo_login.py auth"
echo ""
echo "🖥️ Desktop-Apps verfügbar:"
echo "- Goodix Fingerprint Enrollment (in Anwendungen)"
echo "- Goodix Fingerprint Test (in Anwendungen)"
echo ""
echo "⌨️ Tastenkombination einrichten:"
echo "1. Einstellungen → Tastatur → Tastenkombinationen"
echo "2. Neue Tastenkombination hinzufügen:"
echo "   Name: Goodix Unlock"
echo "   Befehl: /home/mikail/.config/goodix/goodix_unlock.sh"
echo "   Taste: Super+F (oder deine Wahl)"
echo ""
echo "🎉 Dein Goodix-Sensor ist bereit!"
