import subprocess

class PlatformModule:
    def __init__(self):
        self.name = "macOS"
        self.resources = {
            "xcode": "https://developer.apple.com/xcode/",
            "security": "https://support.apple.com/guide/security/welcome/web"
        }
    
    def setup_environment(self):
        commands = [
            "xcode-select --install",
            "/bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"",
            "brew install node",
            "brew install watchman",
            "npm install -g react-native-cli"
        ]
        output = []
        for cmd in commands:
            result = subprocess.run(cmd, shell=True, capture_output=True)
            output.append({
                "command": cmd,
                "status": result.returncode,
                "output": result.stdout.decode(),
                "error": result.stderr.decode()
            })
        return output
    
    def setup_ios_simulator(self):
        return "Open Xcode > Preferences > Components to install simulators"
    
    def get_flutter_path(self):
        return "/usr/local/bin/flutter"