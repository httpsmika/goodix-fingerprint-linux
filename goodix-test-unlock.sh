#!/bin/bash
# Alternative Goodix Unlock - Einfacher Test

echo "🔐 Teste Goodix Unlock direkt..."

# Gehe ins richtige Verzeichnis
cd /home/mikail/goodix-fingerprint-linux

# Starte direkt die Ultra-Simple Version
echo "Führe Goodix-Auth durch..."
if python3 goodix_ultra_simple.py auth; then
    echo "✅ Auth erfolgreich - entsperre Bildschirm..."
    
    # Versuche verschiedene Unlock-Methoden
    dbus-send --session --dest=org.gnome.ScreenSaver --type=method_call /org/gnome/ScreenSaver org.gnome.ScreenSaver.SetActive boolean:false 2>/dev/null
    gnome-screensaver-command --deactivate 2>/dev/null
    loginctl unlock-session 2>/dev/null
    
    notify-send "✅ Goodix Unlock" "Bildschirm entsperrt!" -t 3000
else
    echo "❌ Auth fehlgeschlagen"
    notify-send "❌ Goodix Unlock" "Authentifizierung fehlgeschlagen" -t 3000
fi
