import serial
import usb.core
import subprocess
import logging
from .error_handler import ErrorHandler

class HardwareManager:
    def __init__(self):
        self.logger = logging.getLogger('HardwareManager')
        self.error_handler = ErrorHandler()
        
    def detect_serial_ports(self):
        """Detect available serial ports"""
        ports = []
        try:
            # Linux
            if os.path.exists('/dev'):
                ports = [f"/dev/{f}" for f in os.listdir('/dev') 
                         if f.startswith('ttyUSB') or f.startswith('ttyACM')]
            # Windows
            else:
                import winreg
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DEVICEMAP\SERIALCOMM")
                i = 0
                while True:
                    try:
                        ports.append(winreg.EnumValue(key, i)[1])
                        i += 1
                    except OSError:
                        break
        except Exception as e:
            self.error_handler.handle(e, "detect_serial_ports")
        return ports
    
    def flash_device(self, port, firmware_path):
        """Flash firmware to a device"""
        try:
            # For Arduino
            if firmware_path.endswith('.hex'):
                cmd = f"avrdude -p atmega328p -c arduino -P {port} -U flash:w:{firmware_path}"
                result = subprocess.run(cmd, shell=True, capture_output=True)
                if result.returncode == 0:
                    return "Flashing successful"
                return f"Flashing failed: {result.stderr.decode()}"
            
            # For ESP32
            elif firmware_path.endswith('.bin'):
                cmd = f"esptool.py --port {port} write_flash 0x1000 {firmware_path}"
                result = subprocess.run(cmd, shell=True, capture_output=True)
                if result.returncode == 0:
                    return "Flashing successful"
                return f"Flashing failed: {result.stderr.decode()}"
            
            return "Unsupported firmware format"
        except Exception as e:
            self.error_handler.handle(e, "flash_device")
            return f"Flashing failed: {str(e)}"
    
    def read_sensor_data(self, port, baudrate=9600):
        """Read data from a serial sensor"""
        try:
            with serial.Serial(port, baudrate, timeout=1) as ser:
                data = ser.readline().decode().strip()
                return data
        except Exception as e:
            self.error_handler.handle(e, "read_sensor_data")
            return None
    
    def detect_usb_devices(self):
        """Detect connected USB devices"""
        devices = []
        try:
            for dev in usb.core.find(find_all=True):
                devices.append({
                    "vendor_id": hex(dev.idVendor),
                    "product_id": hex(dev.idProduct),
                    "manufacturer": dev.manufacturer,
                    "product": dev.product
                })
            return devices
        except Exception as e:
            self.error_handler.handle(e, "detect_usb_devices")
            return []