import serial
import subprocess

class EmbeddedTools:
    def __init__(self):
        self.platforms = ["arduino", "raspberrypi", "esp32"]
    
    def flash_arduino(self, sketch_path, port):
        cmd = f"arduino-cli compile --fqbn arduino:avr:uno {sketch_path} && " \
              f"arduino-cli upload -p {port} --fqbn arduino:avr:uno {sketch_path}"
        result = subprocess.run(cmd, shell=True, capture_output=True)
        return result.stdout.decode()
    
    def deploy_to_pi(self, app_path, pi_address):
        cmd = f"scp -r {app_path} pi@{pi_address}:/home/pi/app && " \
              f"ssh pi@{pi_address} 'cd /home/pi/app && python3 main.py'"
        result = subprocess.run(cmd, shell=True, capture_output=True)
        return result.stdout.decode()
    
    def generate_cross_compile_config(self, target):
        return {
            "arduino": {"toolchain": "avr-gcc", "flags": "-mmcu=atmega328p"},
            "raspberrypi": {"toolchain": "arm-linux-gnueabihf-gcc", "flags": "-mfpu=neon"},
            "esp32": {"toolchain": "xtensa-esp32-elf-gcc", "flags": "-mlongcalls"}
        }.get(target, {})