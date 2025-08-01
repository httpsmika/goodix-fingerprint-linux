#!/bin/bash

# USB-Debugging und Analyse-Setup für Goodix Fingerprint Sensor
# Dieses Skript richtet die notwendigen Tools für USB-Analyse ein

echo "=== Goodix Fingerprint Sensor - USB Analysis Setup ==="

# System-Updates
echo "System wird aktualisiert..."
sudo apt update

# USB-Tools installieren
echo "Installiere USB-Analyse-Tools..."
sudo apt install -y \
    usbutils \
    libusb-1.0-0-dev \
    python3-usb \
    wireshark \
    tshark \
    usbmon \
    linux-tools-generic

# Python-Abhängigkeiten
echo "Installiere Python-Abhängigkeiten..."
pip3 install --user \
    pyusb \
    libusb1 \
    construct \
    hexdump

# USB-Monitoring-Setup
echo "Richte USB-Monitoring ein..."

# usbmon Modul laden
sudo modprobe usbmon

# USB-Berechtigungen für User setzen
sudo usermod -a -G dialout $USER
echo 'SUBSYSTEM=="usb", MODE="0666"' | sudo tee /etc/udev/rules.d/99-usb-permissions.rules

# Wireshark-Berechtigungen
sudo usermod -a -G wireshark $USER

echo ""
echo "=== Setup abgeschlossen! ==="
echo ""
echo "Bitte loggen Sie sich erneut ein, damit die Gruppenberechtigungen wirksam werden."
echo ""
echo "Verfügbare Tools:"
echo "  - lsusb: USB-Devices auflisten"
echo "  - wireshark: USB-Traffic aufzeichnen"
echo "  - python3 tools/device_scanner.py: Goodix-Device scannen"
echo "  - python3 analysis/protocol_analyzer.py: Protokoll analysieren"
echo ""
echo "WARNUNG: USB-Debugging erfordert Root-Rechte für manche Operationen!"
