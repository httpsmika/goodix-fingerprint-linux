# Goodix Fingerprint Sensor Commands Reference

## USB-Debugging-Kommandos

### USB-Device Information
```bash
# Alle USB-Devices auflisten
lsusb

# Detaillierte Info über Goodix-Device
lsusb -v -d 27c6:55a2

# USB-Tree anzeigen
lsusb -t

# USB-Device-Pfad finden
find /sys/bus/usb/devices -name "*27C6*" -o -name "*55A2*"
```

### USB-Monitoring
```bash
# USB-Monitor starten (Root-Rechte erforderlich)
sudo modprobe usbmon
sudo tshark -i usbmon1 -w usb_capture.pcap

# Live USB-Traffic anzeigen
sudo tshark -i usbmon1

# Nur Traffic für Goodix-Device
sudo tshark -i usbmon1 -f "usb.device_address == X"  # X durch tatsächliche Adresse ersetzen
```

### Python-Tools
```bash
# Device scannen
python3 tools/device_scanner.py

# Protokoll-Analyse (VORSICHT!)
python3 analysis/protocol_analyzer.py

# Dependencies installieren
pip3 install -r requirements.txt
```

## Reverse Engineering Workflow

### 1. Hardware-Identifikation
1. USB-IDs überprüfen: `lsusb`
2. Device-Descriptors lesen: `lsusb -v -d 27c6:55a2`
3. Interface-Konfiguration analysieren

### 2. Windows-Treiber-Analyse
1. Windows-Treiber-Dateien beschaffen
2. INF-Datei analysieren für Registry-Einstellungen
3. DLL-Dateien mit Tools wie Ghidra/IDA analysieren

### 3. USB-Traffic-Capture
1. USB-Monitoring unter Windows mit USBPcap/Wireshark
2. Normale Fingerabdruck-Operationen durchführen
3. Traffic-Patterns analysieren

### 4. Protokoll-Reverse-Engineering
1. Kommando-Strukturen identifizieren
2. Response-Patterns analysieren
3. Initialisierungs-Sequenz rekonstruieren

### 5. Linux-Implementierung
1. pyusb-basierte Proof-of-Concept
2. libfprint-Treiber entwickeln
3. Integration und Tests

## Sicherheitshinweise

⚠️ **WARNUNG**: 
- USB-Debugging kann Devices beschädigen
- Immer Backups erstellen
- Mit VM und USB-Passthrough testen
- Nie unbekannte Kommandos an Hardware senden

## Nützliche Links

- [libfprint GitHub](https://github.com/freedesktop/libfprint)
- [USB Specification](https://www.usb.org/documents)
- [PyUSB Documentation](https://pyusb.github.io/pyusb/)
- [Wireshark USB Capture](https://wiki.wireshark.org/CaptureSetup/USB)
