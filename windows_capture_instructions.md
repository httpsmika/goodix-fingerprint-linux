
# Windows USB-Traffic-Capture Anweisungen

## Methode 1: USBPcap + Wireshark (Empfohlen)

### Installation:
1. USBPcap herunterladen: https://desowin.org/usbpcap/
2. Wireshark installieren: https://www.wireshark.org/
3. Beide als Administrator installieren

### Capture durchführen:
1. **Wireshark als Administrator starten**
2. **Interface auswählen**: USBPcap1, USBPcap2, etc.
3. **Filter setzen**: `usb.device_address == X` (X = Device-Adresse)
4. **Capture starten** vor Fingerabdruck-Operationen
5. **Fingerabdruck-Aktionen durchführen**:
   - Finger auflegen
   - Finger entfernen  
   - Mehrere Scans
   - Verschiedene Finger
6. **Capture stoppen und speichern** als .pcap/.pcapng

### Wichtige Aktionen zu capturen:
- [ ] System-Boot (Treiber-Initialisierung)
- [ ] Erster Fingerabdruck-Scan
- [ ] Erfolgreicher Scan
- [ ] Fehlgeschlagener Scan
- [ ] Fingerabdruck-Enrollment
- [ ] Fingerabdruck-Verification
- [ ] Standby/Resume-Zyklen

## Methode 2: Windows Performance Toolkit (WPT)

### Setup:
```cmd
# Als Administrator
wpa.exe -profile USB
```

### Trace sammeln:
```cmd
wpr.exe -start USB
# Fingerabdruck-Operationen durchführen
wpr.exe -stop usb_trace.etl
```

## Methode 3: Device Monitor (DevMon)

### Setup:
1. DevMon herunterladen (Sysinternals)
2. Als Administrator starten
3. Filter auf Goodix-Device setzen

## Nach dem Capture:

### 1. Dateien kopieren:
- usb_capture_init.pcap
- usb_capture_scan.pcap  
- usb_capture_enroll.pcap
- usb_capture_verify.pcap

### 2. Windows-Treiber sammeln:
```cmd
# Treiber-Dateien finden
dir C:\Windows\System32\drivers\*goodix*
dir C:\Windows\System32\DriverStore\FileRepository\*goodix*

# Registry-Export
reg export "HKLM\SYSTEM\CurrentControlSet\Services" goodix_services.reg
reg export "HKLM\SYSTEM\CurrentControlSet\Enum\USB\VID_27C6&PID_55A2" goodix_device.reg
```

### 3. Dateien nach Linux übertragen:
- USB-Stick
- Network-Share  
- Cloud-Storage
- Email (für kleine Dateien)

## Wichtige Hinweise:

⚠️ **Administrator-Rechte erforderlich** für USB-Capture
⚠️ **Antivirus temporär deaktivieren** (kann Traffic beeinflussen)
⚠️ **Mehrere Captures** verschiedener Szenarien sammeln
⚠️ **Original-Verhalten dokumentieren** vor jedem Capture

## Typische Capture-Größen:
- Initialisierung: ~1-5 KB
- Ein Scan: ~10-50 KB  
- Enrollment: ~100-500 KB
- Komplette Session: ~1-5 MB
