# devos_linux.py - Linux-specific module
"""
DEVSYS LINUX DEVELOPMENT MODULE
"""

import tkinter as tk
from tkinter import ttk
import os
import subprocess

class LinuxModule:
    def __init__(self, app):
        self.app = app
        self.resources = {
            "os_dev": "https://wiki.osdev.org/",
            "shell_scripting": "https://labex.io/tutorials/linux-how-to-develop-linux-shell-scripts-391578",
            "security": "https://www.netguru.com/blog/web-development-security"
        }
    
    def create_os_dev_tab(self, parent):
        """Create Linux-specific OS development tools"""
        frame = ttk.LabelFrame(parent, text="Linux Development Tools")
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Button(frame, text="Setup Dev Environment", 
                  command=self.setup_environment).pack(pady=5)
        ttk.Button(frame, text="Kernel Build Tools", 
                  command=self.open_kernel_tools).pack(pady=5)
        ttk.Button(frame, text="Containerization", 
                  command=self.open_container_tools).pack(pady=5)
        
        # WSL configuration panel
        wsl_frame = ttk.LabelFrame(frame, text="Windows Subsystem for Linux")
        wsl_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(wsl_frame, text="Configure WSL", 
                  command=self.configure_wsl).pack(side=tk.LEFT, padx=5)
    
    def setup_environment(self):
        """Setup Linux development environment :cite[1]"""
        commands = [
            "sudo apt update && sudo apt upgrade -y",
            "sudo apt install build-essential git",
            "sudo apt install python3 python3-pip",
            "sudo apt install nodejs npm",
            "curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -",
            "echo 'deb https://dl.yarnpkg.com/debian/ stable main' | sudo tee /etc/apt/sources.list.d/yarn.list",
            "sudo apt update && sudo apt install yarn"
        ]
        for cmd in commands:
            subprocess.run(cmd, shell=True)
    
    def open_kernel_tools(self):
        """Open kernel development tools"""
        # Implementation would include kernel build configuration
        pass
    
    def open_container_tools(self):
        """Open container management tools"""
        # Implementation for Docker/LXC management
        pass
    
    def configure_wsl(self):
        """Configure Windows Subsystem for Linux :cite[6]"""
        subprocess.run("wsl --install", shell=True)
        subprocess.run("wsl --set-default-version 2", shell=True)
    
    def new_project(self):
        """Create new Linux project"""
        # Implementation for Linux project setup
        pass