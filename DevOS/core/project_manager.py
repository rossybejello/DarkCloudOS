import os
import json
import yaml
import logging
from datetime import datetime
from pathlib import Path
from .error_handler import ErrorHandler

class ProjectManager:
    PROJECT_TYPES = ["os", "web", "mobile", "cloud", "embedded", "blockchain"]
    
    def __init__(self, application):
        self.app = application
        self.current_project = None
        self.logger = logging.getLogger('ProjectManager')
        self.error_handler = ErrorHandler()
        
    def create_project(self, name, project_type, path=None):
        """Create a new project"""
        try:
            if not path:
                path = os.path.join("projects", name)
                
            os.makedirs(path, exist_ok=True)
            
            # Create project structure
            Path(os.path.join(path, "src")).mkdir(exist_ok=True)
            Path(os.path.join(path, "config")).mkdir(exist_ok=True)
            Path(os.path.join(path, "docs")).mkdir(exist_ok=True)
            Path(os.path.join(path, "tests")).mkdir(exist_ok=True)
            
            # Project configuration
            config = {
                "name": name,
                "type": project_type,
                "created": datetime.now().isoformat(),
                "last_modified": datetime.now().isoformat(),
                "dependencies": [],
                "build_config": {},
                "deployment_targets": []
            }
            
            # Type-specific initialization
            if project_type == "os":
                config["build_config"] = {"target_arch": "x86_64", "bootloader": "GRUB"}
                self._init_os_project(path)
            elif project_type == "web":
                config["dependencies"] = ["node", "npm"]
                self._init_web_project(path)
            
            # Save project config
            with open(os.path.join(path, "project.json"), "w") as f:
                json.dump(config, f, indent=2)
                
            self.current_project = config
            self.current_project["path"] = path
            
            self.app.notifications.success(
                "Project Created", 
                f"Created {name} project at {path}"
            )
            return True
        except Exception as e:
            self.error_handler.handle(e, "create_project")
            return False
            
    def _init_os_project(self, path):
        """Initialize OS project structure"""
        # Create kernel entry point
        with open(os.path.join(path, "src", "kernel.c"), "w") as f:
            f.write("""#include <stdint.h>
#include <stddef.h>

/* Kernel entry point */
void kmain() {
    // TODO: Initialize kernel
    while(1);
}""")
            
        # Create linker script
        with open(os.path.join(path, "src", "linker.ld"), "w") as f:
            f.write("""ENTRY(kmain)

SECTIONS {
    . = 1M;
    .text : { *(.text) }
    .data : { *(.data) }
    .bss : { *(.bss) }
}""")
            
        # Create Makefile
        with open(os.path.join(path, "Makefile"), "w") as f:
            f.write("""# OS Kernel Makefile

CC = gcc
CFLAGS = -ffreestanding -nostdlib -Wall -Wextra

SRC = src/kernel.c
OBJ = $(SRC:.c=.o)

.PHONY: all clean

all: kernel.bin

kernel.bin: $(OBJ)
	$(CC) -T src/linker.ld -o $@ $(CFLAGS) $^
	grub-mkrescue -o os.iso isodir

%.o: %.c
	$(CC) -c $< -o $@ $(CFLAGS)

clean:
	rm -f $(OBJ) kernel.bin os.iso
""")
    
    def _init_web_project(self, path):
        """Initialize web project structure"""
        # Create package.json
        with open(os.path.join(path, "package.json"), "w") as f:
            json.dump({
                "name": "web-project",
                "version": "1.0.0",
                "scripts": {
                    "start": "react-scripts start",
                    "build": "react-scripts build",
                    "test": "react-scripts test"
                },
                "dependencies": {
                    "react": "^18.2.0",
                    "react-dom": "^18.2.0"
                }
            }, f, indent=2)
            
        # Create basic React app
        os.makedirs(os.path.join(path, "src", "components"), exist_ok=True)
        with open(os.path.join(path, "src", "App.js"), "w") as f:
            f.write("""import React from 'react';

function App() {
  return (
    <div className="App">
      <h1>Hello DevOS Toolkit!</h1>
    </div>
  );
}

export default App;""")
    
    def load_project(self, path):
        """Load an existing project"""
        try:
            config_path = os.path.join(path, "project.json")
            if not os.path.exists(config_path):
                raise FileNotFoundError("Project config not found")
                
            with open(config_path, "r") as f:
                config = json.load(f)
                config["path"] = path
                self.current_project = config
                
            self.app.notifications.info(
                "Project Loaded", 
                f"Loaded {config['name']} project"
            )
            return True
        except Exception as e:
            self.error_handler.handle(e, "load_project")
            return False
            
    def save_project(self):
        """Save current project configuration"""
        if not self.current_project:
            return False
            
        try:
            config_path = os.path.join(self.current_project["path"], "project.json")
            self.current_project["last_modified"] = datetime.now().isoformat()
            
            with open(config_path, "w") as f:
                json.dump(self.current_project, f, indent=2)
                
            self.app.notifications.success(
                "Project Saved", 
                f"Saved {self.current_project['name']} project"
            )
            return True
        except Exception as e:
            self.error_handler.handle(e, "save_project")
            return False
            
    def build_project(self):
        """Build the current project"""
        if not self.current_project:
            return False
            
        try:
            project_type = self.current_project["type"]
            
            if project_type == "os":
                return self._build_os_project()
            elif project_type == "web":
                return self._build_web_project()
                
            return False
        except Exception as e:
            self.error_handler.handle(e, "build_project")
            return False
            
    def _build_os_project(self):
        """Build OS project"""
        path = self.current_project["path"]
        result = subprocess.run("make", cwd=path, shell=True, capture_output=True)
        
        if result.returncode == 0:
            self.app.notifications.success(
                "Build Successful", 
                "OS kernel built successfully"
            )
            return True
        else:
            self.app.notifications.error(
                "Build Failed", 
                f"OS build failed: {result.stderr.decode()}"
            )
            return False
            
    def _build_web_project(self):
        """Build web project"""
        path = self.current_project["path"]
        result = subprocess.run("npm run build", cwd=path, shell=True, capture_output=True)
        
        if result.returncode == 0:
            self.app.notifications.success(
                "Build Successful", 
                "Web application built successfully"
            )
            return True
        else:
            self.app.notifications.error(
                "Build Failed", 
                f"Web build failed: {result.stderr.decode()}"
            )
            return False