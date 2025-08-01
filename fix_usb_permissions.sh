#!/bin/bash
# Goodix USB-Berechtigung und Protokoll-Fix

echo "🔧 Goodix USB-Setup und Protokoll-Optimierung"
echo "=============================================="

# 1. USB-Berechtigungen für User setzen
echo "📋 Richte USB-Berechtigungen ein..."

# udev-Regel für Goodix-Sensor erstellen
sudo tee /etc/udev/rules.d/99-goodix-sensor.rules > /dev/null << 'EOF'
# Goodix Fingerprint Sensor 27C6:55A2
# Erlaubt Zugriff für alle User in der plugdev-Gruppe
SUBSYSTEM=="usb", ATTR{idVendor}=="27c6", ATTR{idProduct}=="55a2", MODE="0666", GROUP="plugdev"
SUBSYSTEM=="usb", ATTR{idVendor}=="27C6", ATTR{idProduct}=="55A2", MODE="0666", GROUP="plugdev"

# Alternative für direkte Device-Berechtigung
KERNEL=="hidraw*", ATTRS{idVendor}=="27c6", ATTRS{idProduct}=="55a2", MODE="0666", GROUP="plugdev"
EOF

# 2. User zur plugdev-Gruppe hinzufügen
echo "👤 Füge Benutzer zur plugdev-Gruppe hinzu..."
sudo usermod -a -G plugdev $USER

# 3. udev-Regeln neu laden
echo "🔄 Lade udev-Regeln neu..."
sudo udevadm control --reload-rules
sudo udevadm trigger

# 4. USB-Device neu erkennen
echo "🔍 Erkenne USB-Devices neu..."
# USB-Device trennen und neu verbinden (simuliert)
echo "   (Ziehen Sie den USB-Connector kurz ab und stecken ihn wieder ein)"

echo ""
echo "✅ USB-Setup abgeschlossen!"
echo ""
echo "📋 Nächste Schritte:"
echo "1. USB-Connector kurz ab- und wieder anstecken"
echo "2. Terminal neu starten oder neu einloggen (für Gruppenmitgliedschaft)"
echo "3. Ohne sudo testen: ./goodix_login.py test"
echo "4. Fingerabdruck registrieren: ./goodix_login.py enroll"
echo ""
echo "💡 Falls weiterhin Probleme:"
echo "   - Prüfen: groups \$USER (sollte 'plugdev' enthalten)"
echo "   - USB-Berechtigungen: ls -la /dev/bus/usb/*/(*Ihre Device-ID*)"
