"""
Goodix Fingerprint Sensor USB Device Scanner

Dieses Modul scannt nach Goodix-Fingerabdrucksensoren und sammelt
grundlegende Informationen über das USB-Device.
"""

import usb.core
import usb.util
import logging

# Goodix Vendor/Product IDs
GOODIX_VENDOR_ID = 0x27C6
TARGET_PRODUCT_ID = 0x55A2

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GoodixDeviceScanner:
    """Scanner für Goodix-Fingerabdrucksensoren"""
    
    def __init__(self):
        self.device = None
    
    def find_device(self):
        """Sucht nach dem Goodix-Sensor"""
        logger.info(f"Suche nach Goodix-Device {GOODIX_VENDOR_ID:04x}:{TARGET_PRODUCT_ID:04x}")
        
        # Suche nach dem spezifischen Device
        self.device = usb.core.find(idVendor=GOODIX_VENDOR_ID, idProduct=TARGET_PRODUCT_ID)
        
        if self.device is None:
            logger.error("Goodix-Sensor nicht gefunden!")
            return False
        
        logger.info("Goodix-Sensor gefunden!")
        return True
    
    def get_device_info(self):
        """Sammelt Informationen über das Device"""
        if self.device is None:
            logger.error("Kein Device gefunden!")
            return None
        
        info = {
            'vendor_id': self.device.idVendor,
            'product_id': self.device.idProduct,
            'device_class': self.device.bDeviceClass,
            'device_subclass': self.device.bDeviceSubClass,
            'device_protocol': self.device.bDeviceProtocol,
            'configurations': self.device.bNumConfigurations,
            'bus': self.device.bus,
            'address': self.device.address,
        }
        
        try:
            info['manufacturer'] = usb.util.get_string(self.device, self.device.iManufacturer)
            info['product'] = usb.util.get_string(self.device, self.device.iProduct)
            info['serial'] = usb.util.get_string(self.device, self.device.iSerialNumber)
        except Exception as e:
            logger.warning(f"Konnte String-Descriptors nicht lesen: {e}")
            info['manufacturer'] = "Unbekannt"
            info['product'] = "Unbekannt" 
            info['serial'] = "Unbekannt"
        
        return info
    
    def scan_configurations(self):
        """Scannt alle Konfigurationen und Interfaces"""
        if self.device is None:
            logger.error("Kein Device gefunden!")
            return None
        
        configs = []
        
        for cfg in self.device:
            config_info = {
                'config_value': cfg.bConfigurationValue,
                'interfaces': []
            }
            
            for intf in cfg:
                interface_info = {
                    'interface_number': intf.bInterfaceNumber,
                    'alternate_setting': intf.bAlternateSetting,
                    'interface_class': intf.bInterfaceClass,
                    'interface_subclass': intf.bInterfaceSubClass,
                    'interface_protocol': intf.bInterfaceProtocol,
                    'endpoints': []
                }
                
                for ep in intf:
                    endpoint_info = {
                        'address': ep.bEndpointAddress,
                        'attributes': ep.bmAttributes,
                        'max_packet_size': ep.wMaxPacketSize,
                        'interval': ep.bInterval,
                        'direction': 'IN' if usb.util.endpoint_direction(ep.bEndpointAddress) == usb.util.ENDPOINT_IN else 'OUT'
                    }
                    interface_info['endpoints'].append(endpoint_info)
                
                config_info['interfaces'].append(interface_info)
            
            configs.append(config_info)
        
        return configs

def main():
    """Hauptfunktion zum Testen des Scanners"""
    scanner = GoodixDeviceScanner()
    
    if scanner.find_device():
        info = scanner.get_device_info()
        print("\n=== Device Information ===")
        for key, value in info.items():
            print(f"{key}: {value}")
        
        configs = scanner.scan_configurations()
        print("\n=== Configurations ===")
        for i, config in enumerate(configs):
            print(f"\nConfiguration {i+1}:")
            print(f"  Value: {config['config_value']}")
            for j, intf in enumerate(config['interfaces']):
                print(f"  Interface {j}: Number={intf['interface_number']}, "
                      f"Class={intf['interface_class']}, "
                      f"Subclass={intf['interface_subclass']}, "
                      f"Protocol={intf['interface_protocol']}")
                for k, ep in enumerate(intf['endpoints']):
                    print(f"    Endpoint {k}: Address=0x{ep['address']:02x}, "
                          f"Direction={ep['direction']}, "
                          f"MaxPacket={ep['max_packet_size']}")

if __name__ == "__main__":
    main()
