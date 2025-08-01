# Reverse Engineering Fortschritt

## Überblick
Dokumentation der Erkenntnisse beim Reverse Engineering des Goodix-Fingerabdrucksensors (27C6:55A2).

## Hardware-Details
- **Vendor ID**: 27C6 (Goodix Technology Inc.)
- **Product ID**: 55A2
- **Interface**: USB 2.0
- **Klasse**: Vendor Specific

## USB-Analyse

### Device Descriptor
```
Vendor ID: 0x27C6 (10182) - Goodix Technology Inc.
Product ID: 0x55A2 (21922) - Target Sensor
Device Class: 0xFF (239) - Vendor Specific
Device Subclass: 0x02 (2)
Device Protocol: 0x01 (1)
Configurations: 1
USB Bus: 3, Address: 3
```

### Interface und Endpoints
```
Configuration 1:
  Value: 1
  Interface 0: 
    Number: 0
    Class: 0xFF (255) - Vendor Specific
    Subclass: 0x00 (0)
    Protocol: 0x00 (0)
    
  Endpoints:
    OUT Endpoint: 0x01 (Direction: OUT, MaxPacket: 512)
    IN Endpoint:  0x82 (Direction: IN,  MaxPacket: 512)
```

## Protokoll-Analyse

### Initialisierung
```
TODO: Initialisierungssequenz dokumentieren
```

### Kommando-Struktur
```
TODO: Kommando-Format und Responses
```

### Fingerabdruck-Scan-Prozess
```
TODO: Ablauf eines Fingerabdruck-Scans
```

## Wichtige Erkenntnisse

### Erfolgreiche Kommandos
- [ ] Device-Status abfragen
- [ ] Version/Firmware-Info
- [ ] Sensor initialisieren
- [ ] Scan starten/stoppen
- [ ] Bild-Daten lesen

### Fehlgeschlagene Versuche
- TODO: Dokumentation fehlgeschlagener Ansätze

## Windows-Treiber-Analyse

### Treiber-Dateien
- TODO: Analyse der Windows-Treiber-Dateien
- TODO: INF-Datei-Analyse
- TODO: DLL-Reverse Engineering

### Registry-Einträge
- TODO: Relevante Registry-Schlüssel

## Nächste Schritte

1. **USB-Traffic-Capture**: Wireshark/USBPcap unter Windows
2. **Treiber-Disassembly**: Reverse Engineering der Windows-Treiber
3. **Protokoll-Rekonstruktion**: Nachbau der Kommunikation
4. **libfprint-Integration**: Implementierung als libfprint-Treiber

## Referenzen

- [libfprint Documentation](https://fprint.freedesktop.org/)
- [USB Specification](https://www.usb.org/documents)
- [Goodix Technology](https://www.goodix.com/)

## Warnungen

⚠️ **ACHTUNG**: Experimentelle Hardware-Zugriffe können das Device beschädigen!
⚠️ **ACHTUNG**: Nur mit entsprechenden Berechtigungen und Vorsichtsmaßnahmen durchführen!
