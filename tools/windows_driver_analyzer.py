"""
Windows Driver Analysis Tool für Goodix Fingerprint Sensor

Dieses Tool hilft bei der Analyse von Windows-Treiber-Dateien
und extrahiert wichtige Informationen für das Reverse Engineering.
"""

import os
import re
import subprocess
import tempfile
from pathlib import Path

class WindowsDriverAnalyzer:
    """Analysiert Windows-Treiber-Dateien"""
    
    def __init__(self):
        self.driver_dir = "windows_drivers"
        self.analysis_dir = "driver_analysis"
        
    def setup_directories(self):
        """Erstellt Analyse-Verzeichnisse"""
        os.makedirs(self.driver_dir, exist_ok=True)
        os.makedirs(self.analysis_dir, exist_ok=True)
        
    def generate_driver_collection_guide(self):
        """Erstellt Anleitung zum Sammeln von Treiber-Dateien"""
        
        guide = """
# Windows Treiber-Sammlung für Goodix Sensor

## 1. Treiber-Dateien lokalisieren

### Device Manager Methode:
1. **Device Manager öffnen** (devmgmt.msc)
2. **Biometric devices** oder **Unknown devices** erweitern
3. **Goodix-Device** finden (27C6:55A2)
4. **Rechtsklick → Properties → Driver → Driver Details**
5. **Dateipfade notieren**

### PowerShell Methode:
```powershell
# Als Administrator ausführen
Get-PnpDevice | Where-Object {$_.InstanceId -like "*VID_27C6&PID_55A2*"}
Get-PnpDeviceProperty -InstanceId "USB\\VID_27C6&PID_55A2\\*"
```

## 2. Typische Treiber-Speicherorte

### System32 Treiber:
```cmd
dir C:\\Windows\\System32\\drivers\\*goodix*
dir C:\\Windows\\System32\\drivers\\*finger*
dir C:\\Windows\\System32\\drivers\\*biometric*
```

### DriverStore:
```cmd
dir C:\\Windows\\System32\\DriverStore\\FileRepository\\*goodix* /s
dir C:\\Windows\\System32\\DriverStore\\FileRepository\\*27c6* /s
```

### WinSxS:
```cmd
dir C:\\Windows\\WinSxS\\*goodix* /s
dir C:\\Windows\\WinSxS\\*biometric* /s
```

## 3. Zu sammelnde Dateien

### Treiber-Binaries:
- [ ] .sys Dateien (Kernel-Treiber)
- [ ] .dll Dateien (User-Mode Libraries)
- [ ] .exe Dateien (Service/Tools)

### Konfiguration:
- [ ] .inf Dateien (Installation)
- [ ] .cat Dateien (Katalog)
- [ ] .ini/.cfg Dateien (Konfiguration)

### Registry-Exports:
```cmd
# Device-spezifische Registry
reg export "HKLM\\SYSTEM\\CurrentControlSet\\Enum\\USB\\VID_27C6&PID_55A2" goodix_device.reg

# Service-Registry  
reg export "HKLM\\SYSTEM\\CurrentControlSet\\Services" goodix_services.reg

# Biometric Framework
reg export "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Biometric" biometric.reg
```

## 4. Erweiterte Sammlung

### Firmware-Dateien:
```cmd
dir C:\\Windows\\System32\\* /s | findstr -i goodix
dir C:\\ProgramData\\*goodix* /s
dir "C:\\Program Files"\\*goodix* /s
dir "C:\\Program Files (x86)"\\*goodix* /s
```

### Event Logs:
```powershell
Get-WinEvent -LogName System | Where-Object {$_.Message -like "*goodix*"}
Get-WinEvent -LogName Application | Where-Object {$_.Message -like "*goodix*"}
```

### WDF Traces (wenn verfügbar):
```cmd
# Windows Driver Framework Logs
dir C:\\Windows\\System32\\LogFiles\\WDF\\* 
```

## 5. Sicherheits-Kopie erstellen

### Backup-Ordner:
```cmd
mkdir C:\\GoodixBackup
xcopy "C:\\Windows\\System32\\drivers\\*goodix*" C:\\GoodixBackup\\ /s /e
xcopy "C:\\Windows\\System32\\DriverStore\\FileRepository\\*goodix*" C:\\GoodixBackup\\ /s /e
```

### ZIP-Archiv erstellen:
```powershell
Compress-Archive -Path C:\\GoodixBackup\\* -DestinationPath C:\\GoodixDrivers.zip
```

## 6. Nach Linux übertragen

### Methoden:
- USB-Stick
- Network Share (SMB/CIFS)
- Cloud Storage (OneDrive, Google Drive)
- SCP/SSH (wenn verfügbar)

### Ziel-Verzeichnis: ./windows_drivers/

## ⚠️ Wichtige Hinweise:

- **Administrator-Rechte** für Treiber-Zugriff erforderlich
- **Original-Dateien NIEMALS modifizieren**
- **Immer Backups erstellen** vor Experimenten
- **Antivirus** kann Zugriff blockieren (temporär deaktivieren)
- **Digitale Signaturen** beachten (Code-Signing)

## 7. Copyright-Hinweise:

⚠️ **RECHTLICHER HINWEIS:**
- Treiber-Dateien sind urheberrechtlich geschützt
- Nur für private Reverse-Engineering-Zwecke nutzen
- Nicht weiterverbreiten oder kommerziell nutzen
- Bei Unsicherheit: Anwalt konsultieren
"""
        return guide

    def analyze_inf_file(self, inf_path):
        """Analysiert INF-Datei"""
        
        if not os.path.exists(inf_path):
            return None
            
        analysis = {
            'hardware_ids': [],
            'services': [],
            'registry_keys': [],
            'files': [],
            'version_info': {}
        }
        
        try:
            with open(inf_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            # Hardware IDs extrahieren
            hw_pattern = r'USB\\VID_([0-9A-F]{4})&PID_([0-9A-F]{4})'
            analysis['hardware_ids'] = re.findall(hw_pattern, content, re.IGNORECASE)
            
            # Services extrahieren
            service_pattern = r'AddService\s*=\s*([^,]+)'
            analysis['services'] = re.findall(service_pattern, content, re.IGNORECASE)
            
            # Registry-Einträge
            reg_pattern = r'HKR[^\\n]+'
            analysis['registry_keys'] = re.findall(reg_pattern, content)
            
            # Version-Informationen
            version_section = re.search(r'\[Version\](.*?)\[', content, re.DOTALL)
            if version_section:
                for line in version_section.group(1).split('\n'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        analysis['version_info'][key.strip()] = value.strip()
                        
        except Exception as e:
            print(f"Fehler beim Analysieren der INF-Datei: {e}")
            
        return analysis

    def generate_analysis_report(self, inf_analysis=None):
        """Generiert Analyse-Bericht"""
        
        report = """
# Windows Treiber-Analyse Bericht

## Gesammelte Dateien

### Zu analysierende Dateien:
- [ ] .inf Dateien (Installation/Konfiguration)
- [ ] .sys Dateien (Kernel-Treiber)  
- [ ] .dll Dateien (User-Mode Bibliotheken)
- [ ] Registry-Exports (.reg Dateien)

### Analyse-Tools:

#### 1. Static Analysis:
```bash
# Strings extrahieren
strings goodix_driver.sys > goodix_strings.txt

# Hex-Dump
hexdump -C goodix_driver.sys > goodix_hexdump.txt

# File-Info
file goodix_driver.sys
```

#### 2. Reverse Engineering Tools:
- **Ghidra** (NSA, kostenlos): https://ghidra-sre.org/
- **IDA Free** (Begrenzt): https://hex-rays.com/ida-free/
- **Radare2** (Open Source): https://rada.re/
- **x64dbg** (Windows Debugger): https://x64dbg.com/

#### 3. Windows-spezifische Tools:
- **PEiD** (PE-Analyse)
- **Resource Hacker** (Ressourcen)
- **Dependency Walker** (DLL-Dependencies)
- **Process Monitor** (Runtime-Analyse)

### Typische Analyse-Schritte:

1. **PE-Header analysieren** (.exe/.dll/.sys)
2. **Import/Export Tables** untersuchen
3. **Strings extrahieren** (USB-Kommandos, Error-Messages)
4. **Entry Points** identifizieren
5. **USB-I/O-Funktionen** lokalisieren
6. **Protokoll-Konstanten** finden

## ⚠️ Reverse Engineering Ethik:

- **Nur für Interoperabilität** (Linux-Treiber-Entwicklung)
- **Keine Copyright-Verletzung**
- **Clean-Room-Implementation** verwenden
- **Eigene Implementierung** basierend auf Protokoll-Verständnis

"""
        
        if inf_analysis:
            report += f"""
## INF-Datei-Analyse:

### Hardware IDs:
{chr(10).join([f"- VID_{vid}, PID_{pid}" for vid, pid in inf_analysis['hardware_ids']])}

### Services:
{chr(10).join([f"- {service}" for service in inf_analysis['services']])}

### Version Info:
{chr(10).join([f"- {key}: {value}" for key, value in inf_analysis['version_info'].items()])}
"""
        
        return report

def main():
    """Hauptfunktion"""
    analyzer = WindowsDriverAnalyzer()
    analyzer.setup_directories()
    
    print("=== Windows Driver Analysis Setup ===")
    
    # Guide erstellen
    guide = analyzer.generate_driver_collection_guide()
    with open("windows_driver_collection_guide.md", "w", encoding="utf-8") as f:
        f.write(guide)
    print("✓ Treiber-Sammlungs-Guide erstellt: windows_driver_collection_guide.md")
    
    # Analyse-Bericht
    report = analyzer.generate_analysis_report()
    with open("driver_analysis_template.md", "w", encoding="utf-8") as f:
        f.write(report)
    print("✓ Analyse-Template erstellt: driver_analysis_template.md")
    
    print("\n=== Nächste Schritte ===")
    print("1. windows_driver_collection_guide.md befolgen")
    print("2. Treiber-Dateien nach ./windows_drivers/ kopieren")
    print("3. INF-Dateien mit diesem Tool analysieren")
    print("4. Reverse-Engineering-Tools für .sys/.dll-Dateien nutzen")

if __name__ == "__main__":
    main()
