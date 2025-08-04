class GenericPlatform:
    def __init__(self):
        self.name = "Generic"
        self.resources = {
            "os_dev": "https://wiki.osdev.org/",
            "security": "https://owasp.org/"
        }
    
    def setup_environment(self):
        return "Generic platform setup - please install dependencies manually"
    
    def create_os_image(self, config):
        return "echo 'OS image creation not implemented for generic platform'"