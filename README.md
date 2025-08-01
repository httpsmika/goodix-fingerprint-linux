# Goodix Fingerprint Sensor Reverse Engineering Project

Dieses Projekt zielt darauf ab, den Goodix-Fingerabdrucksensor (27C6:55A2) unter Linux zum Laufen zu bringen durch Reverse Engineering und Treiber-Entwicklung.

## Sensor Details
- **Vendor ID**: 27C6
- **Product ID**: 55A2
- **Hersteller**: Goodix
- **Status**: Nicht offiziell von libfprint unterstützt

## Projektstruktur

```
├── analysis/           # USB-Protokoll-Analyse und Captures
├── drivers/           # Treiber-Entwicklung und Tests
├── libfprint_integration/  # Integration mit libfprint
├── tools/             # Hilfstools und Skripte
├── docs/              # Dokumentation und Erkenntnisse
└── samples/           # Beispiel-Code und Referenzen
```

## Erste Schritte

1. **USB-Analyse**: Sammeln von USB-Traffic-Daten
2. **Protokoll-Verstehen**: Reverse Engineering der Kommunikation
3. **Treiber-Entwicklung**: Implementierung eines funktionsfähigen Treibers
4. **libfprint-Integration**: Integration in das bestehende Framework

## Abhängigkeiten

- Python 3.8+
- libusb
- libfprint (für Integration)
- Wireshark/tshark (für USB-Analyse)
- USB-Debugging-Tools

## Warnung

Dieses Projekt beinhaltet experimentelle Treiber-Entwicklung. Verwenden Sie es auf eigene Gefahr und stellen Sie sicher, dass Sie Backups haben.
