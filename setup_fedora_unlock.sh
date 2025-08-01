#!/bin/bash
# Fedora GNOME Fingerprint Unlock Setup

echo "🔐 Goodix Fingerprint Unlock Setup für Fedora"
echo "=============================================="
echo ""

# Prüfe ob goodix_success.py funktioniert
echo "1️⃣ Teste Goodix Authentication System..."
if ! python3 /home/mikail/goodix-fingerprint-linux/goodix_success.py auth >/dev/null 2>&1; then
    echo "❌ Goodix Authentication System nicht bereit!"
    echo "💡 Führe zuerst aus: python3 goodix_success.py enroll"
    exit 1
fi
echo "✅ Goodix Authentication System funktioniert!"

# Desktop Entry für Applications erstellen
echo ""
echo "2️⃣ Erstelle Desktop Entry..."
mkdir -p ~/.local/share/applications

cat > ~/.local/share/applications/goodix-unlock.desktop << 'EOF'
[Desktop Entry]
Name=Goodix Fingerprint Unlock
Comment=Entsperre Bildschirm mit Fingerabdruck
Exec=/home/mikail/goodix-fingerprint-linux/goodix-unlock-fixed.sh
Icon=fingerprint
Terminal=false
Type=Application
Categories=System;Security;
Keywords=fingerprint;unlock;biometric;goodix
EOF

echo "✅ Desktop Entry erstellt: ~/.local/share/applications/goodix-unlock.desktop"

# Prüfe ob Script ausführbar ist
echo ""
echo "3️⃣ Prüfe Script-Berechtigungen..."
chmod +x /home/mikail/goodix-fingerprint-linux/goodix-unlock-fixed.sh
echo "✅ Script ist ausführbar"

echo ""
echo "🎉 Setup abgeschlossen!"
echo ""
echo "📖 Anleitung:"
echo "============"
echo ""
echo "METHODE 1 - Über Activities (Einfachste Methode):"
echo "  1. Drücke Super-Taste (Windows-Taste)"
echo "  2. Tippe: 'Goodix'"
echo "  3. Klicke auf 'Goodix Fingerprint Unlock'"
echo ""
echo "METHODE 2 - Tastenkombination einrichten:"
echo "  1. Öffne GNOME Einstellungen"
echo "  2. Gehe zu 'Tastatur' → 'Tastenkombinationen anzeigen und anpassen'"
echo "  3. Scrolle nach unten zu 'Benutzerdefinierte Tastenkombinationen'"
echo "  4. Klicke '+' für neue Tastenkombination"
echo "  5. Name: 'Goodix Unlock'"
echo "  6. Befehl: /home/mikail/goodix-fingerprint-linux/goodix-unlock-fixed.sh"
echo "  7. Tastenkombination: Super+F (oder andere Wahl)"
echo ""
echo "METHODE 3 - Terminal-Befehl:"
echo "  /home/mikail/goodix-fingerprint-linux/goodix-unlock-fixed.sh"
echo ""
echo "💡 Nach dem Entsperren wird eine Benachrichtigung angezeigt!"
