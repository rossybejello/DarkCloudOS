import subprocess
import os

class OSBuilder:
    @staticmethod
    def build_os_image(config):
        """Build an OS image based on configuration"""
        if config["type"] == "linux":
            return "Building Linux image... (Simulated)"
        elif config["type"] == "unikernel":
            return OSBuilder.build_unikernel(config)
        return "Unsupported OS type"
    
    @staticmethod
    def build_unikernel(config):
        """Build a unikernel image"""
        commands = [
            f"mkdir -p {config['output_dir']}",
            f"cd {config['project_dir']}",
            "make build"
        ]
        return subprocess.run(" && ".join(commands), shell=True, capture_output=True)
    
    @staticmethod
    def build_framework_project(config):
        """Build a project using a specific framework"""
        framework = config["framework"]
        project_dir = config["project_dir"]
        
        if framework == "react":
            return OSBuilder.build_react_project(project_dir)
        elif framework == "react_native":
            return OSBuilder.build_react_native_project(project_dir, config["platform"])
        elif framework == "flutter":
            return OSBuilder.build_flutter_project(project_dir, config["platform"])
        return f"Unsupported framework: {framework}"
    
    @staticmethod
    def build_react_project(project_dir):
        commands = [
            f"cd {project_dir}",
            "npm install",
            "npm run build"
        ]
        return subprocess.run(" && ".join(commands), shell=True, capture_output=True)
    
    @staticmethod
    def build_react_native_project(project_dir, platform="android"):
        commands = [
            f"cd {project_dir}",
            "npm install",
            f"npx react-native run-{platform}"
        ]
        return subprocess.run(" && ".join(commands), shell=True, capture_output=True)
    
    @staticmethod
    def build_flutter_project(project_dir, platform="android"):
        commands = [
            f"cd {project_dir}",
            "flutter pub get",
            f"flutter build {platform}"
        ]
        return subprocess.run(" && ".join(commands), shell=True, capture_output=True)

class ContainerBuilder:
    @staticmethod
    def create_container(config):
        """Create a container based on configuration"""
        if config["type"] == "docker":
            return ContainerBuilder.create_docker_container(config)
        elif config["type"] == "unikernel":
            return ContainerBuilder.create_unikernel_container(config)
        return "Unsupported container type"
    
    @staticmethod
    def create_docker_container(config):
        commands = [
            f"cd {config['project_dir']}",
            "docker build -t myapp .",
            "docker run -d myapp"
        ]
        return subprocess.run(" && ".join(commands), shell=True, capture_output=True)
    
    @staticmethod
    def create_unikernel_container(config):
        runtime = config.get("runtime", "osv")
        if runtime == "osv":
            return f"capstan build -p {config['project_dir']}"
        elif runtime == "includeos":
            return f"docker run -v {config['project_dir']}:/app includeos/includeos"
        return "Unsupported unikernel runtime"