<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Copilot Instructions für Goodix Fingerprint Sensor Projekt

## Projektkontext
Dies ist ein Reverse-Engineering-Projekt für einen Goodix-Fingerabdrucksensor (27C6:55A2) unter Linux. Das Ziel ist die Entwicklung eines funktionsfähigen Treibers und die Integration in libfprint.

## Code-Generierungs-Richtlinien

### USB-Kommunikation
- Verwende libusb-basierte Implementierungen für direkte Hardware-Kommunikation
- Priorisiere asynchrone USB-Transfers für bessere Performance
- Implementiere robuste Fehlerbehandlung für USB-Timeouts und -Fehler

### Treiber-Entwicklung
- Folge den libfprint-Konventionen und -Strukturen
- Implementiere alle erforderlichen Callback-Funktionen
- Verwende GObject-Patterns für Speicherverwaltung

### Sicherheit
- Implementiere Bounds-Checking für alle Pufferzugriffe
- Validiere alle Eingabedaten von der Hardware
- Verwende sichere Speicherallokation und -freigabe

### Debugging und Logging
- Nutze strukturiertes Logging für USB-Kommunikation
- Implementiere Hex-Dump-Funktionen für Protokoll-Analyse
- Füge ausführliche Kommentare für Reverse-Engineering-Erkenntnisse hinzu

### Code-Stil
- Verwende konsistente Namenskonventionen (goodix_sensor_*)
- Kommentiere alle Magic Numbers mit ihrer Bedeutung
- Dokumentiere Protokoll-Details in Code-Kommentaren
