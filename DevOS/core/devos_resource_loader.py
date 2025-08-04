import importlib
import platform
import json
import os

class ResourceLoader:
    RESOURCE_DIR = "devos_resources"
    
    def __init__(self):
        os.makedirs(self.RESOURCE_DIR, exist_ok=True)
        self.ensure_resource_files()
    
    def ensure_resource_files(self):
        """Create resource files if missing"""
        resources = {
            "frameworks.json": {
                "react": {
                    "docs": "https://react.dev/learn",
                    "security": "https://react-security.dev/",
                    "os_integration": "https://github.com/neutralinojs/neutralinojs-react"
                },
                "react_native": {
                    "core": "https://reactnative.dev/",
                    "security": "https://reactnative.dev/docs/security",
                    "os_integration": "https://github.com/react-native-community/cli"
                },
                "jetpack_compose": {
                    "docs": "https://developer.android.com/jetpack/compose",
                    "security": "https://developer.android.com/topic/security",
                    "native": "https://kotlinlang.org/docs/native-overview.html"
                },
                "flutter": {
                    "core": "https://flutter.dev/docs",
                    "desktop": "https://flutter.dev/desktop",
                    "os_embedding": "https://pub.dev/packages/embedder"
                },
                "kotlin": {
                    "compose": "https://developer.android.com/jetpack/compose",
                    "native": "https://kotlinlang.org/docs/native-overview.html",
                    "security": "https://kotlinlang.org/docs/security.html"
                }
            },
            "security.json": {
                "web": {
                    "owasp": "https://owasp.org/www-project-top-ten/",
                    "csp": "https://content-security-policy.com/",
                    "headers": "https://securityheaders.com/"
                },
                "os": {
                    "hardening": "https://github.com/trimstray/linux-hardening-checklist",
                    "selinux": "https://selinuxproject.org/",
                    "apparmor": "https://apparmor.net/"
                },
                "cross_platform": {
                    "data_encryption": "https://cryptography.io/en/latest/",
                    "secure_storage": "https://www.openssl.org/",
                    "auth": "https://oauth.net/"
                }
            }
        }
        
        for filename, content in resources.items():
            path = os.path.join(self.RESOURCE_DIR, filename)
            if not os.path.exists(path):
                with open(path, 'w') as f:
                    json.dump(content, f, indent=2)
    
    def detect_platform(self):
        return platform.system()
    
    def load_platform_module(self, os_name):
        try:
            module_name = f"devos_platform_{os_name.lower()}"
            spec = importlib.util.find_spec(module_name)
            if spec is None:
                raise ImportError(f"Module {module_name} not found")
            module = importlib.import_module(module_name)
            return module.PlatformModule()
        except ImportError:
            # Fallback to generic platform
            from devos_platform_generic import GenericPlatform
            return GenericPlatform()
    
    def load_framework_resources(self, framework):
        path = os.path.join(self.RESOURCE_DIR, "frameworks.json")
        with open(path) as f:
            frameworks = json.load(f)
            return frameworks.get(framework.lower(), {})
    
    def load_security_resources(self, domain):
        path = os.path.join(self.RESOURCE_DIR, "security.json")
        with open(path) as f:
            security = json.load(f)
            return security.get(domain, {})