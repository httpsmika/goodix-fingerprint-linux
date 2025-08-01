#!/bin/bash
# Goodix Desktop Login Integration
# Erweitert Ihr Desktop-Login um Fingerabdruck-Authentifizierung

set -e

GOODIX_LOGIN="/home/mikail/Fingerabdrucksensor/goodix_login.py"
USER=${USER:-$(whoami)}

# Farben für Output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔐 Goodix Desktop Login Integration${NC}"
echo "=================================="

# Funktionen
show_help() {
    echo "Verwendung: $0 [OPTION]"
    echo ""
    echo "Optionen:"
    echo "  setup         - Desktop-Integration einrichten"
    echo "  enroll        - Fingerabdruck registrieren"
    echo "  login         - Fingerabdruck-Login testen"
    echo "  unlock        - Bildschirm mit Fingerabdruck entsperren"
    echo "  install       - System-Installation (sudo erforderlich)"
    echo "  uninstall     - System-Installation entfernen"
    echo "  help          - Diese Hilfe anzeigen"
    echo ""
    echo "Beispiele:"
    echo "  $0 setup      # Desktop-Integration einrichten"
    echo "  $0 enroll     # Fingerabdruck registrieren"
    echo "  $0 login      # Login testen"
}

check_goodix_sensor() {
    echo -e "${YELLOW}🔍 Prüfe Goodix-Sensor...${NC}"
    
    if python3 "$GOODIX_LOGIN" test 2>/dev/null; then
        echo -e "${GREEN}✅ Goodix-Sensor gefunden und funktionsfähig${NC}"
        return 0
    else
        echo -e "${RED}❌ Goodix-Sensor nicht verfügbar${NC}"
        echo "   Mögliche Ursachen:"
        echo "   - Sensor nicht angeschlossen"
        echo "   - Keine USB-Berechtigung (sudo erforderlich)"
        echo "   - Treiber-Problem"
        return 1
    fi
}

enroll_fingerprint() {
    echo -e "${BLUE}📋 Fingerabdruck-Registrierung${NC}"
    echo "==============================="
    
    if ! check_goodix_sensor; then
        return 1
    fi
    
    echo -e "${YELLOW}👆 Starte Fingerabdruck-Registrierung für Benutzer: $USER${NC}"
    
    if python3 "$GOODIX_LOGIN" enroll "$USER"; then
        echo -e "${GREEN}🎉 Fingerabdruck erfolgreich registriert!${NC}"
        return 0
    else
        echo -e "${RED}❌ Registrierung fehlgeschlagen${NC}"
        return 1
    fi
}

test_login() {
    echo -e "${BLUE}🔐 Fingerabdruck-Login Test${NC}"
    echo "==========================="
    
    if ! check_goodix_sensor; then
        return 1
    fi
    
    echo -e "${YELLOW}👆 Teste Fingerabdruck-Login für Benutzer: $USER${NC}"
    
    if python3 "$GOODIX_LOGIN" auth "$USER"; then
        echo -e "${GREEN}✅ Login erfolgreich!${NC}"
        
        # Optional: Desktop-Notification
        if command -v notify-send >/dev/null 2>&1; then
            notify-send "Goodix Login" "✅ Fingerabdruck-Login erfolgreich!" --icon=dialog-information
        fi
        
        return 0
    else
        echo -e "${RED}❌ Login fehlgeschlagen${NC}"
        
        if command -v notify-send >/dev/null 2>&1; then
            notify-send "Goodix Login" "❌ Fingerabdruck-Login fehlgeschlagen!" --icon=dialog-error
        fi
        
        return 1
    fi
}

unlock_screen() {
    echo -e "${BLUE}🔓 Bildschirm-Entsperrung${NC}"
    echo "========================"
    
    # GUI-Dialog anzeigen (falls verfügbar)
    if command -v zenity >/dev/null 2>&1; then
        zenity --info --text="👆 Finger auf Goodix-Sensor legen..." --timeout=2 &
    fi
    
    if python3 "$GOODIX_LOGIN" auth "$USER"; then
        echo -e "${GREEN}✅ Bildschirm entsperrt!${NC}"
        
        # Bildschirm entsperren (abhängig vom Desktop-Environment)
        if command -v gnome-screensaver-command >/dev/null 2>&1; then
            gnome-screensaver-command --deactivate 2>/dev/null || true
        elif command -v xscreensaver-command >/dev/null 2>&1; then
            xscreensaver-command -deactivate 2>/dev/null || true
        elif command -v loginctl >/dev/null 2>&1; then
            loginctl unlock-session 2>/dev/null || true
        fi
        
        # Success-Notification
        if command -v notify-send >/dev/null 2>&1; then
            notify-send "Goodix Unlock" "🔓 Bildschirm entsperrt!" --icon=dialog-information
        fi
        
        return 0
    else
        echo -e "${RED}❌ Entsperrung fehlgeschlagen${NC}"
        
        if command -v notify-send >/dev/null 2>&1; then
            notify-send "Goodix Unlock" "❌ Entsperrung fehlgeschlagen!" --icon=dialog-error
        fi
        
        return 1
    fi
}

setup_desktop_integration() {
    echo -e "${BLUE}🖥️ Desktop-Integration Setup${NC}"
    echo "============================"
    
    # Desktop-Shortcut erstellen
    DESKTOP_FILE="$HOME/.local/share/applications/goodix-login.desktop"
    
    mkdir -p "$(dirname "$DESKTOP_FILE")"
    
    cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Name=Goodix Fingerprint Login
Comment=Fingerabdruck-Authentifizierung mit Goodix-Sensor
Exec=$PWD/desktop_goodix_login.sh login
Icon=fingerprint
Terminal=true
Type=Application
Categories=System;Security;
EOF
    
    echo -e "${GREEN}✅ Desktop-Shortcut erstellt: $DESKTOP_FILE${NC}"
    
    # Autostart-Entry (optional)
    AUTOSTART_FILE="$HOME/.config/autostart/goodix-unlock.desktop"
    
    read -p "📱 Autostart für Bildschirm-Entsperrung einrichten? (j/n): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[JjYy]$ ]]; then
        mkdir -p "$(dirname "$AUTOSTART_FILE")"
        
        cat > "$AUTOSTART_FILE" << EOF
[Desktop Entry]
Name=Goodix Screen Unlock
Comment=Ermöglicht Bildschirm-Entsperrung mit Fingerabdruck
Exec=$PWD/desktop_goodix_login.sh unlock
Icon=fingerprint
Terminal=false
Type=Application
X-GNOME-Autostart-enabled=true
Hidden=false
EOF
        
        echo -e "${GREEN}✅ Autostart-Entry erstellt: $AUTOSTART_FILE${NC}"
    fi
    
    # Tastenkürzel-Info
    echo ""
    echo -e "${YELLOW}💡 Empfohlene Tastenkürzel (manuell einrichten):${NC}"
    echo "   Strg+Alt+F: Fingerabdruck-Login"
    echo "   Strg+Alt+U: Bildschirm entsperren"
    echo ""
    echo "   Kommando für Login: $PWD/desktop_goodix_login.sh login"
    echo "   Kommando für Unlock: $PWD/desktop_goodix_login.sh unlock"
}

install_system_wide() {
    echo -e "${BLUE}⚙️ System-Installation${NC}"
    echo "===================="
    
    if [ "$EUID" -ne 0 ]; then
        echo -e "${RED}❌ Root-Rechte erforderlich für System-Installation${NC}"
        echo "Führen Sie aus: sudo $0 install"
        return 1
    fi
    
    # Scripts nach /usr/local/bin kopieren
    cp "$GOODIX_LOGIN" /usr/local/bin/goodix-login
    cp "$0" /usr/local/bin/goodix-desktop
    chmod +x /usr/local/bin/goodix-login
    chmod +x /usr/local/bin/goodix-desktop
    
    # udev-Regel für USB-Berechtigung
    cat > /etc/udev/rules.d/99-goodix-fingerprint.rules << EOF
# Goodix Fingerprint Sensor (27C6:55A2)
SUBSYSTEM=="usb", ATTR{idVendor}=="27c6", ATTR{idProduct}=="55a2", MODE="0666", GROUP="plugdev"
EOF
    
    # udev-Regeln neu laden
    udevadm control --reload-rules
    udevadm trigger
    
    echo -e "${GREEN}✅ System-Installation abgeschlossen${NC}"
    echo "📋 Verfügbare Kommandos:"
    echo "   goodix-login enroll  - Fingerabdruck registrieren"
    echo "   goodix-login auth    - Authentifizierung testen" 
    echo "   goodix-desktop login - Desktop-Login"
    echo "   goodix-desktop unlock - Bildschirm entsperren"
}

# Hauptlogik
case "${1:-help}" in
    "setup")
        setup_desktop_integration
        ;;
    "enroll")
        enroll_fingerprint
        ;;
    "login")
        test_login
        ;;
    "unlock")
        unlock_screen
        ;;
    "install")
        install_system_wide
        ;;
    "uninstall")
        sudo rm -f /usr/local/bin/goodix-login /usr/local/bin/goodix-desktop
        sudo rm -f /etc/udev/rules.d/99-goodix-fingerprint.rules
        echo -e "${GREEN}✅ System-Installation entfernt${NC}"
        ;;
    "help"|"--help"|"-h")
        show_help
        ;;
    *)
        echo -e "${RED}❌ Unbekannte Option: $1${NC}"
        show_help
        exit 1
        ;;
esac
