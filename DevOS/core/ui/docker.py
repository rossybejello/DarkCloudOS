import docker
from core.auth_manager import AuthManager
from core.error_handler import ErrorHandler

class DockerIntegration:
    def __init__(self, application):
        self.app = application
        self.auth = application.auth_manager
        self.error_handler = ErrorHandler()
        self.client = None
        
    def connect(self):
        """Connect to Docker Hub"""
        credentials = self.auth.get_credentials("dockerhub")
        if not credentials:
            return False
            
        try:
            self.client = docker.from_env()
            
            # Authenticate if needed
            if "username" in credentials and "password" in credentials:
                self.client.login(
                    username=credentials["username"],
                    password=credentials["password"],
                    registry="https://hub.docker.com"
                )
            return True
        except Exception as e:
            self.error_handler.handle(e, "docker_connect")
            return False
            
    def build_image(self, path, tag):
        """Build Docker image"""
        if not self.client:
            if not self.connect():
                return False
                
        try:
            image, logs = self.client.images.build(path=path, tag=tag)
            return image.id
        except Exception as e:
            self.error_handler.handle(e, "docker_build")
            return False
            
    def push_image(self, tag):
        """Push image to Docker Hub"""
        if not self.client:
            if not self.connect():
                return False
                
        try:
            response = self.client.images.push(tag)
            return "success" in response.lower()
        except Exception as e:
            self.error_handler.handle(e, "docker_push")
            return False