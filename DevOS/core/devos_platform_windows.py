import subprocess

class PlatformModule:
    def __init__(self):
        self.name = "Windows"
        self.resources = {
            "wsl": "https://learn.microsoft.com/en-us/windows/wsl/",
            "security": "https://docs.microsoft.com/en-us/windows/security/"
        }
    
    def setup_environment(self):
        commands = [
            "wsl --install",
            "wsl --set-default-version 2",
            "winget install -e --id Microsoft.VisualStudio.2022.Enterprise"
        ]
        results = []
        for cmd in commands:
            result = subprocess.run(cmd, shell=True, capture_output=True)
            results.append({
                "command": cmd,
                "status": result.returncode,
                "output": result.stdout.decode(),
                "error": result.stderr.decode()
            })
        return results
    
    def setup_android_studio(self):
        return "Download Android Studio from https://developer.android.com/studio"
    
    def get_flutter_path(self):
        return r"C:\src\flutter\bin\flutter.bat"