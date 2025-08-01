
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
Get-PnpDeviceProperty -InstanceId "USB\VID_27C6&PID_55A2\*"
```

## 2. Typische Treiber-Speicherorte

### System32 Treiber:
```cmd
dir C:\Windows\System32\drivers\*goodix*
dir C:\Windows\System32\drivers\*finger*
dir C:\Windows\System32\drivers\*biometric*
```

### DriverStore:
```cmd
dir C:\Windows\System32\DriverStore\FileRepository\*goodix* /s
dir C:\Windows\System32\DriverStore\FileRepository\*27c6* /s
```

### WinSxS:
```cmd
dir C:\Windows\WinSxS\*goodix* /s
dir C:\Windows\WinSxS\*biometric* /s
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
reg export "HKLM\SYSTEM\CurrentControlSet\Enum\USB\VID_27C6&PID_55A2" goodix_device.reg

# Service-Registry  
reg export "HKLM\SYSTEM\CurrentControlSet\Services" goodix_services.reg

# Biometric Framework
reg export "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Biometric" biometric.reg
```

## 4. Erweiterte Sammlung

### Firmware-Dateien:
```cmd
dir C:\Windows\System32\* /s | findstr -i goodix
dir C:\ProgramData\*goodix* /s
dir "C:\Program Files"\*goodix* /s
dir "C:\Program Files (x86)"\*goodix* /s
```

### Event Logs:
```powershell
Get-WinEvent -LogName System | Where-Object {$_.Message -like "*goodix*"}
Get-WinEvent -LogName Application | Where-Object {$_.Message -like "*goodix*"}
```

### WDF Traces (wenn verfügbar):
```cmd
# Windows Driver Framework Logs
dir C:\Windows\System32\LogFiles\WDF\* 
```

## 5. Sicherheits-Kopie erstellen

### Backup-Ordner:
```cmd
mkdir C:\GoodixBackup
xcopy "C:\Windows\System32\drivers\*goodix*" C:\GoodixBackup\ /s /e
xcopy "C:\Windows\System32\DriverStore\FileRepository\*goodix*" C:\GoodixBackup\ /s /e
```

### ZIP-Archiv erstellen:
```powershell
Compress-Archive -Path C:\GoodixBackup\* -DestinationPath C:\GoodixDrivers.zip
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
