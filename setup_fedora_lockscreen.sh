#!/bin/bash
# Goodix GNOME Sperrbildschirm Integration für Fedora

set -e

echo "🔐 Goodix GNOME Sperrbildschirm Setup für Fedora"
echo "==============================================="

# 1. Prüfe ob GNOME läuft
if ! pgrep -x "gnome-shell" > /dev/null; then
    echo "❌ GNOME Shell läuft nicht. Dieses Script ist für GNOME gedacht."
    exit 1
fi

echo "✅ GNOME Shell erkannt"

# 2. Installiere GNOME-spezifische Tools
echo "📦 Installiere GNOME-Tools..."
sudo dnf install -y gnome-tweaks dconf-editor

# 3. Erstelle Goodix Unlock Script
echo "🔓 Erstelle GNOME Unlock Script..."

cat > /tmp/goodix-gnome-unlock << 'EOF'
#!/bin/bash
# Goodix GNOME Sperrbildschirm Entsperrung

export DISPLAY=:0
export WAYLAND_DISPLAY=wayland-0

USER=${1:-$USER}

# Zeige Notification
notify-send "🔐 Goodix Fingerprint" "Initialisiere Sensor..." -t 3000

if /usr/local/bin/goodix-login auth "$USER" 2>/dev/null; then
    # Erfolgreiche Authentifizierung
    notify-send "✅ Fingerprint Login" "Willkommen zurück, $USER!" -t 3000
    
    # GNOME Bildschirm entsperren
    # Für X11
    if [ -n "$DISPLAY" ]; then
        gnome-screensaver-command --deactivate 2>/dev/null || true
    fi
    
    # Für Wayland
    if [ -n "$WAYLAND_DISPLAY" ]; then
        # Wayland entsperren (neuere GNOME Versionen)
        busctl --user call org.gnome.ScreenSaver /org/gnome/ScreenSaver org.gnome.ScreenSaver SetActive b false 2>/dev/null || true
        # Alternative für ältere Versionen
        dbus-send --session --dest=org.gnome.ScreenSaver --type=method_call /org/gnome/ScreenSaver org.gnome.ScreenSaver.SetActive boolean:false 2>/dev/null || true
    fi
    
    exit 0
else
    # Fehlgeschlagene Authentifizierung
    notify-send "❌ Fingerprint Login" "Authentifizierung fehlgeschlagen" -t 3000
    exit 1
fi
EOF

sudo mv /tmp/goodix-gnome-unlock /usr/local/bin/goodix-gnome-unlock
sudo chmod +x /usr/local/bin/goodix-gnome-unlock

# 4. Erstelle Desktop-Verknüpfung für manuellen Unlock
echo "🖥️ Erstelle Desktop-Integration..."

cat > ~/.local/share/applications/goodix-unlock.desktop << 'EOF'
[Desktop Entry]
Name=Goodix Fingerprint Unlock
Comment=Unlock screen with Goodix fingerprint sensor
Exec=/usr/local/bin/goodix-gnome-unlock
Icon=input-fingerprint
Type=Application
Categories=System;Security;
NoDisplay=false
EOF

# 5. Erstelle Keyboard Shortcut Setup
echo "⌨️ Erstelle Tastenkürzel-Setup..."

cat > /tmp/setup-goodix-shortcut.sh << 'EOF'
#!/bin/bash
# Setup Goodix Keyboard Shortcut

echo "🔧 Setup Tastenkürzel für Goodix Unlock..."

# GNOME Tastenkürzel hinzufügen
# Dieser Befehl muss vom Benutzer ausgeführt werden (nicht als root)

gsettings set org.gnome.settings-daemon.plugins.media-keys custom-keybindings "['/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/goodix-unlock/']"

gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/goodix-unlock/ name 'Goodix Fingerprint Unlock'

gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/goodix-unlock/ command '/usr/local/bin/goodix-gnome-unlock'

gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/goodix-unlock/ binding '<Super>f'

echo "✅ Tastenkürzel eingerichtet: Super+F"
EOF

chmod +x /tmp/setup-goodix-shortcut.sh
mv /tmp/setup-goodix-shortcut.sh ~/.local/bin/setup-goodix-shortcut.sh

# 6. Teste Hardware
echo "🧪 Teste Hardware-Verbindung..."
if ./diagnose_goodix.py > /tmp/goodix-test.log 2>&1; then
    echo "✅ Hardware-Test erfolgreich"
else
    echo "⚠️ Hardware-Test mit Warnungen (siehe /tmp/goodix-test.log)"
fi

# 7. User-Setup-Instruktionen
echo ""
echo "🎯 Setup abgeschlossen! Nächste Schritte:"
echo ""
echo "1. 📝 BENUTZER REGISTRIEREN:"
echo "   ./goodix_demo_login.py enroll $USER"
echo ""
echo "2. 🧪 TESTEN:"
echo "   ./goodix_demo_login.py auth $USER"
echo ""
echo "3. ⌨️ TASTENKÜRZEL EINRICHTEN:"
echo "   ~/.local/bin/setup-goodix-shortcut.sh"
echo ""
echo "4. 🔓 SPERRBILDSCHIRM TESTEN:"
echo "   - Bildschirm sperren: Super+L"
echo "   - Mit Fingerprint entsperren: Super+F"
echo "   - Oder: Applications → Goodix Fingerprint Unlock"
echo ""
echo "5. 🔄 NACH NEUSTART:"
echo "   - Neu einloggen für Gruppenmitgliedschaft"
echo "   - USB-Sensor ab- und anstecken"
echo ""
echo "🎉 Fedora GNOME Sperrbildschirm-Integration bereit!"
echo ""
echo "💡 VERWENDUNG:"
echo "   - Bildschirm sperren wie gewohnt"
echo "   - Super+F drücken für Fingerprint-Unlock"
echo "   - Oder Anwendung 'Goodix Fingerprint Unlock' starten"
