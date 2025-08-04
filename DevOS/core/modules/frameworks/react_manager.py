import subprocess
import os
from core.error_handler import ErrorHandler

class ReactFrameworkManager:
    def __init__(self):
        self.error_handler = ErrorHandler()
        
    def create_react_app(self, app_name="my-app"):
        """Create a new React application"""
        try:
            if not os.path.exists(app_name):
                os.makedirs(app_name)
                
            commands = [
                f"cd {app_name}",
                "npx create-react-app .",
                "npm install"
            ]
            
            result = subprocess.run(
                " && ".join(commands),
                shell=True,
                check=True,
                capture_output=True,
                text=True
            )
            
            return {
                'success': True,
                'message': "React app created successfully",
                'path': os.path.abspath(app_name)
            }
        except subprocess.CalledProcessError as e:
            self.error_handler.handle(e)
            return {
                'success': False,
                'message': f"Failed to create React app: {e.stderr}"
            }
            
    def run_react_native(self, platform, project_path=None):
        """Run React Native app on target platform"""
        if not project_path:
            project_path = os.getcwd()
            
        try:
            commands = [
                f"cd {project_path}",
                f"npx react-native run-{platform}"
            ]
            
            result = subprocess.run(
                " && ".join(commands),
                shell=True,
                check=True,
                capture_output=True,
                text=True
            )
            
            return {
                'success': True,
                'message': f"React Native app running on {platform}",
                'output': result.stdout
            }
        except subprocess.CalledProcessError as e:
            self.error_handler.handle(e)
            return {
                'success': False,
                'message': f"Failed to run React Native: {e.stderr}"
            }
    
    # Additional React-specific methods...
