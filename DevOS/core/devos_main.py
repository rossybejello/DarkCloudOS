#!/usr/bin/env python3
"""
DEVSYS MASTER TOOLKIT - CORE APPLICATION
Version 4.0 - Modular Cross-Platform Edition
"""

import os
import sys
import platform
from devos_gui import DevOSGUI
from devos_resource_loader import ResourceLoader
from devos_tracker import DevelopmentTracker
from devos_builder import OSBuilder, ContainerBuilder
from devos_cloud import CloudDeployer
from devos_cicd import CICDGenerator
from devos_embedded import EmbeddedTools
from devos_ai import AIDevelopmentAssistant
from devos_blockchain import BlockchainTools
from devos_monitoring import PerformanceMonitor
from devos_docs import DocumentationGenerator

class DevOSCore:
    def __init__(self):
        self.resource_loader = ResourceLoader()
        self.tracker = DevelopmentTracker()
        self.builder = OSBuilder()
        self.container_builder = ContainerBuilder()
        self.cloud_deployer = CloudDeployer()
        self.cicd_generator = CICDGenerator()
        self.embedded_tools = EmbeddedTools()
        self.ai_assistant = AIDevelopmentAssistant()
        self.blockchain_tools = BlockchainTools()
        self.monitor = PerformanceMonitor()
        self.docs_generator = DocumentationGenerator()
        
        # Detect current platform
        self.current_os = platform.system()
        self.os_module = self.resource_loader.load_platform_module(self.current_os)
        
        # Initialize GUI
        self.gui = DevOSGUI(self)
        
    def run(self):
        self.gui.start_main_loop()
        
    def get_framework_resources(self, framework):
        return self.resource_loader.load_framework_resources(framework)
    
    def get_security_resources(self, domain):
        return self.resource_loader.load_security_resources(domain)
    
    def build_project(self, project_type, config):
        if project_type == "os":
            return self.builder.build_os_image(config)
        elif project_type == "container":
            return self.container_builder.create_container(config)
        elif project_type == "framework":
            return self.builder.build_framework_project(config)
        return "Unknown project type"

if __name__ == "__main__":
    app = DevOSCore()
    app.run()
