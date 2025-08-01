#!/bin/bash
# Goodix System Login Integration
# Integriert den Goodix Demo-Login in das System

set -e

echo "🔐 Goodix System-Login Integration"
echo "=================================="

# 1. System-Installation
echo "📦 Installiere System-Dateien..."

# Demo-Login als System-Login verfügbar machen
sudo cp goodix_demo_login.py /usr/local/bin/goodix-login
sudo chmod +x /usr/local/bin/goodix-login

# 2. Desktop-Integration erstellen
echo "🖥️ Erstelle Desktop-Integration..."

cat > /tmp/goodix-desktop-auth << 'EOF'
#!/bin/bash
# Goodix Desktop Authentication

USER=${1:-$USER}

# Zeige schöne GUI
if command -v zenity >/dev/null 2>&1; then
    zenity --info --text="🔐 Goodix Fingerprint Login\n\nBitte warten Sie auf Hardware-Initialisierung..." --timeout=3
    
    if /usr/local/bin/goodix-login auth "$USER"; then
        zenity --info --text="✅ Fingerprint-Login erfolgreich!\nWillkommen zurück, $USER!" --timeout=3
        exit 0
    else
        zenity --error --text="❌ Fingerprint-Login fehlgeschlagen"
        exit 1
    fi
else
    # Fallback ohne GUI
    echo "🔐 Goodix Fingerprint Login für $USER"
    /usr/local/bin/goodix-login auth "$USER"
fi
EOF

sudo mv /tmp/goodix-desktop-auth /usr/local/bin/goodix-desktop-auth
sudo chmod +x /usr/local/bin/goodix-desktop-auth

# 3. Screen-Unlock Integration
echo "🔓 Erstelle Screen-Unlock Integration..."

cat > /tmp/goodix-unlock << 'EOF'
#!/bin/bash
# Goodix Screen Unlock

if /usr/local/bin/goodix-login auth $USER; then
    echo "✅ Fingerprint unlock successful"
    
    # GNOME Screen unlock
    if command -v gnome-screensaver-command >/dev/null 2>&1; then
        gnome-screensaver-command --deactivate
    fi
    
    # KDE Screen unlock
    if command -v qdbus >/dev/null 2>&1; then
        qdbus org.freedesktop.ScreenSaver /ScreenSaver SimulateUserActivity
    fi
    
    exit 0
else
    echo "❌ Fingerprint unlock failed"
    exit 1
fi
EOF

sudo mv /tmp/goodix-unlock /usr/local/bin/goodix-unlock
sudo chmod +x /usr/local/bin/goodix-unlock

# 4. Sudo Integration (Optional)
echo "🔐 Erstelle Sudo-Integration..."

cat > /tmp/99-goodix-sudo << 'EOF'
# Goodix Fingerprint Sudo Integration
# Allows fingerprint authentication for sudo

# Enable fingerprint for sudo (optional)
# Uncomment the next line to enable:
# %wheel ALL=(ALL) EXEC:/usr/local/bin/goodix-desktop-auth %u
EOF

sudo mv /tmp/99-goodix-sudo /etc/sudoers.d/99-goodix-sudo

# 5. Desktop-Dateien erstellen
echo "🖱️ Erstelle Desktop-Verknüpfungen..."

# Enrollment Desktop Entry
cat > ~/.local/share/applications/goodix-enroll.desktop << 'EOF'
[Desktop Entry]
Name=Goodix Fingerprint Enrollment
Comment=Register your fingerprint with Goodix sensor
Exec=gnome-terminal -- /usr/local/bin/goodix-login enroll %u
Icon=input-fingerprint
Type=Application
Categories=System;Security;
EOF

# Authentication Test Desktop Entry  
cat > ~/.local/share/applications/goodix-test.desktop << 'EOF'
[Desktop Entry]
Name=Goodix Fingerprint Test
Comment=Test fingerprint authentication
Exec=gnome-terminal -- /usr/local/bin/goodix-desktop-auth %u
Icon=input-fingerprint
Type=Application
Categories=System;Security;
EOF

# Update desktop database
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database ~/.local/share/applications/
fi

echo ""
echo "✅ Installation abgeschlossen!"
echo ""
echo "🎯 Verfügbare Kommandos:"
echo "   goodix-login enroll [user]     - Fingerprint registrieren"
echo "   goodix-login auth [user]       - Fingerprint-Login testen"
echo "   goodix-desktop-auth [user]     - GUI-Fingerprint-Login"
echo "   goodix-unlock                  - Screen entsperren"
echo ""
echo "🖥️ Desktop-Integration:"
echo "   - Anwendungsmenü: 'Goodix Fingerprint Enrollment'"
echo "   - Anwendungsmenü: 'Goodix Fingerprint Test'"
echo ""
echo "🔧 Nächste Schritte:"
echo "1. Testen Sie: goodix-desktop-auth"
echo "2. Für PAM-Integration: Siehe docs/fingerprint_login_setup.md"
echo "3. Für GDM-Integration: Weitere Konfiguration erforderlich"
echo ""
echo "🎉 Ihr Goodix-Sensor ist bereit für System-Login!"
