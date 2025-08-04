# devos_resources.py - Resource management
"""
DEVSYS RESOURCE MANAGEMENT MODULE
"""

import json
import os

class ResourceManager:
    def __init__(self):
        self.resource_file = "devos_resources.json"
        self.init_resources()
    
    def init_resources(self):
        """Initialize resource database"""
        if not os.path.exists(self.resource_file):
            resources = {
                "os_dev": {
                    "Linux": "https://wiki.osdev.org/",
                    "Windows": "https://learn.microsoft.com/en-us/windows/dev-environment/",
                    "macOS": "https://developer.apple.com/documentation/"
                },
                "security": {
                    "Web Security": "https://www.netguru.com/blog/web-development-security",
                    "OWASP Top 10": "https://owasp.org/www-project-top-ten/",
                    "Cryptography": "https://cryptography.io/"
                },
                "frameworks": {
                    "Kivy": "https://kivy.org/",
                    "OSv": "http://osv.io/",
                    "Node.js": "https://nodejs.org/en/docs/"
                }
            }
            with open(self.resource_file, 'w') as f:
                json.dump(resources, f, indent=2)
    
    def get_resources(self, category):
        """Get resources by category"""
        with open(self.resource_file, 'r') as f:
            resources = json.load(f)
            return resources.get(category, {})
    
    def add_resource(self, category, name, url):
        """Add new resource"""
        with open(self.resource_file, 'r') as f:
            resources = json.load(f)
        
        if category not in resources:
            resources[category] = {}
        resources[category][name] = url
        
        with open(self.resource_file, 'w') as f:
            json.dump(resources, f, indent=2)