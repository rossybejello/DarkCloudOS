import subprocess
import os
import json
from core.error_handler import ErrorHandler

class ReactManager:
    def __init__(self, application):
        self.app = application
        self.error_handler = ErrorHandler()
        
    def build(self, config):
        """Build a React project"""
        try:
            project_path = config.get('path', os.getcwd())
            commands = [
                f"cd {project_path}",
                "npm install",
                "npm run build"
            ]
            
            result = subprocess.run(
                " && ".join(commands),
                shell=True,
                check=True,
                capture_output=True,
                text=True
            )
            
            self.app.notifications.success(
                "Build Successful",
                "React project built successfully"
            )
            
            return {
                'success': True,
                'message': "Build completed",
                'output': result.stdout
            }
        except subprocess.CalledProcessError as e:
            self.error_handler.handle(e)
            return {
                'success': False,
                'message': f"Build failed: {e.stderr}"
            }
    
    def get_resources(self):
        """Get React resources"""
        return self.app.knowledge_base.get_resource('frameworks', 'react')