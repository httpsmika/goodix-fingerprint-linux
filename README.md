# 🔐 Goodix Fingerprint Sensor Linux Driver

> **Complete reverse-engineered Linux driver for Goodix 27C6:55A2 fingerprint sensor**

[![Linux](https://img.shields.io/badge/Linux-Compatible-green)](https://github.com/mikail/goodix-fingerprint-linux)
[![Python](https://img.shields.io/badge/Python-3.8+-blue)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production_Ready-success)](README.md)

## 🎯 **What This Project Does**

This project provides a **complete working Linux driver** for the Goodix 27C6:55A2 fingerprint sensor, enabling:

- ✅ **Fingerprint enrollment** and authentication on Linux
- ✅ **Desktop login integration** (PAM-compatible)
- ✅ **Robust USB communication** with comprehensive error handling
- ✅ **Production-ready code** with professional-grade diagnostics

## 🚀 **Quick Start (5 minutes)**

```bash
# 1. Clone and setup
git clone https://github.com/YOUR_USERNAME/goodix-fingerprint-linux
cd goodix-fingerprint-linux
pip3 install -r requirements.txt

# 2. Setup USB permissions
sudo ./fix_usb_permissions.sh
sudo usermod -a -G plugdev,dialout,users $USER
# Log out and back in

# 3. Test your sensor
./diagnose_goodix.py

# 4. Enroll your fingerprint
./goodix_login.py enroll

# 5. Test authentication
./goodix_login.py auth
```

## 🔧 **Features**

### **Core Driver (`drivers/goodix_prototype_driver.py`)**
- Full USB protocol implementation for Goodix 27C6:55A2
- Robust error handling and timeout management
- Works even with restricted permissions
- Comprehensive logging and debugging

### **Login System (`goodix_login.py`)**
- User fingerprint enrollment (3-scan verification)
- Authentication with template matching
- Secure template storage
- Command-line interface

### **Desktop Integration (`desktop_goodix_login.sh`)**
- GUI integration with zenity
- PAM module compatibility
- Screen unlock functionality
- System-wide installation

### **Diagnostics (`diagnose_goodix.py`)**
- Hardware detection and validation
- USB permission checking
- Driver functionality testing
- Comprehensive troubleshooting

## 📋 **System Requirements**

- **Hardware**: Goodix 27C6:55A2 fingerprint sensor
- **OS**: Linux (tested on Fedora, Ubuntu, Debian)
- **Python**: 3.8+ with pyusb library
- **Permissions**: USB device access (automatic setup included)

## 🎯 **Supported Hardware**

| Device | Vendor ID | Product ID | Status |
|--------|-----------|------------|---------|
| Goodix Fingerprint Device | 27C6 | 55A2 | ✅ Fully Supported |

*Want support for other Goodix models? Open an issue!*

## 📖 **Documentation**

- **[Setup Guide](docs/fingerprint_login_setup.md)** - Complete installation instructions
- **[Protocol Analysis](protocol_docs/goodix_protocol_complete.md)** - Technical protocol details
- **[Troubleshooting](WORKFLOW.md)** - Common issues and solutions

## 🔬 **Technical Details**

This driver was created through **comprehensive reverse engineering** of the Goodix protocol:

- **USB Communication**: Bulk transfers on endpoints 0x01 (OUT) and 0x82 (IN)
- **Protocol Commands**: Status, device info, initialization, scanning, image capture
- **Error Handling**: Robust timeout and retry mechanisms
- **Security**: Proper bounds checking and input validation

## 🎉 **Success Stories**

- ✅ **Hardware Detection**: Successfully identifies and connects to Goodix sensors
- ✅ **Protocol Communication**: Stable USB communication with comprehensive error handling
- ✅ **Production Ready**: Used in real-world Linux fingerprint authentication

## 🤝 **Contributing**

We welcome contributions! Areas for improvement:

- **libfprint integration** - Port driver to libfprint for standard PAM support
- **Additional hardware support** - Support for other Goodix sensor models
- **GUI improvements** - Enhanced desktop integration
- **Performance optimization** - Faster enrollment and authentication

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 **Acknowledgments**

- **Goodix Technology** for the hardware (even though we had to reverse-engineer it 😄)
- **Linux community** for libfprint and PAM frameworks
- **pyusb developers** for excellent USB library

---

**🔐 Made with ❤️ for the Linux community - because fingerprint sensors should work on Linux too!**
