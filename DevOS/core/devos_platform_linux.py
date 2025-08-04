import subprocess

class PlatformModule:
    def __init__(self):
        self.name = "Linux"
        self.resources = {
            "kernel_dev": "https://www.kernel.org/doc/html/latest/",
            "container_tools": "https://docs.docker.com/desktop/linux/",
            "security": "https://linux-audit.com/linux-hardening-guide/"
        }
    
    def setup_environment(self):
        commands = [
            "sudo apt update",
            "sudo apt install -y build-essential git",
            "sudo apt install -y python3 python3-pip",
            "sudo apt install -y nodejs npm",
            "sudo npm install -g react-native-cli"
        ]
        for cmd in commands:
            result = subprocess.run(cmd, shell=True, capture_output=True)
            if result.returncode != 0:
                return f"Error in command: {cmd}\n{result.stderr.decode()}"
        return "Linux environment setup complete"
    
    def create_os_image(self, config):
        return "dd if=/dev/zero of=os.img bs=1M count=1024 && mkfs.ext4 os.img"
    
    def get_android_tools(self):
        return {
            "sdk_manager": "sdkmanager --list",
            "avd_manager": "avdmanager list avd",
            "emulator": "emulator -list-avds"
        }