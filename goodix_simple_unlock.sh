#!/bin/bash
# Einfacher Goodix Unlock - Ohne gnome-terminal

echo "🔐 Goodix Unlock gestartet..."

# Zeige Notification
notify-send "🔐 Goodix Unlock" "Starte Fingerabdruck-Authentifizierung..." -t 3000 2>/dev/null &

# Gehe ins richtige Verzeichnis
cd /home/mikail/goodix-fingerprint-linux

echo "🔍 Führe Fingerabdruck-Authentifizierung durch..."
echo "==============================================="

if python3 goodix_ultra_simple.py auth; then
    echo ""
    echo "✅ Authentifizierung erfolgreich!"
    echo "🔓 Versuche Bildschirm zu entsperren..."
    
    # Alle bekannten Unlock-Methoden versuchen
    dbus-send --session --dest=org.gnome.ScreenSaver --type=method_call /org/gnome/ScreenSaver org.gnome.ScreenSaver.SetActive boolean:false 2>/dev/null &
    gnome-screensaver-command --deactivate 2>/dev/null &
    loginctl unlock-session 2>/dev/null &
    
    # GNOME Shell unlock (neuere Versionen)  
    gdbus call --session --dest org.gnome.ScreenSaver --object-path /org/gnome/ScreenSaver --method org.gnome.ScreenSaver.SetActive false 2>/dev/null &
    
    notify-send "✅ Goodix Unlock" "Authentifizierung erfolgreich! Bildschirm entsperrt." -t 3000 2>/dev/null
    echo "🎉 Bildschirm entsperrt!"
    
else
    echo ""
    echo "❌ Authentifizierung fehlgeschlagen!"
    notify-send "❌ Goodix Unlock" "Authentifizierung fehlgeschlagen" -t 3000 2>/dev/null
fi

echo ""
echo "Goodix Unlock beendet."
