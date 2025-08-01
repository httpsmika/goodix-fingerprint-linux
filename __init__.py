"""
Goodix Fingerprint Sensor Analysis Package

Ein Python-Package für die Analyse und Reverse-Engineering
des Goodix-Fingerabdrucksensors 27C6:55A2.
"""

__version__ = "0.1.0"
__author__ = "Reverse Engineering Team"

# USB-IDs
GOODIX_VENDOR_ID = 0x27C6
GOODIX_PRODUCT_ID = 0x55A2

# Logging konfigurieren
import logging
import colorlog

def setup_logging(level=logging.INFO):
    """Konfiguriert strukturiertes Logging für das Projekt"""
    
    handler = colorlog.StreamHandler()
    handler.setFormatter(colorlog.ColoredFormatter(
        '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    ))
    
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(handler)

# Standard-Logging einrichten
setup_logging()
