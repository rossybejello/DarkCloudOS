import logging
import subprocess
import os
from .react_manager import ReactManager
from .flutter_manager import FlutterManager
from .compose_manager import ComposeManager

class FrameworkManager:
    def __init__(self, application):
        self.app = application
        self.logger = logging.getLogger('FrameworkManager')
        self.managers = {
            'react': ReactManager(application),
            'flutter': FlutterManager(application),
            'compose': ComposeManager(application)
        }
        
    def build(self, config):
        """Build a framework project"""
        framework = config.get('framework')
        if framework in self.managers:
            return self.managers[framework].build(config)
        
        self.app.notifications.error(
            "Build Failed",
            f"Unsupported framework: {framework}"
        )
        return {
            'success': False,
            'message': f"Unsupported framework: {framework}"
        }
    
    def get_framework_resources(self, framework):
        """Get resources for a specific framework"""
        if framework in self.managers:
            return self.managers[framework].get_resources()
        return {}