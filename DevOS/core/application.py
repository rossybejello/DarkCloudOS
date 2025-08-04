import os
import sys
import logging
import threading
from .error_handler import ErrorHandler
from .system_scanner import SystemScanner
from .notification import NotificationCenter
from .knowledge_base import KnowledgeBase
from modules import ModuleLoader
from ui import MainWindow
from .project_manager import ProjectManager
from .collaboration import CollaborationServer
from .profiler import PerformanceProfiler
from modules.hardware import HardwareManager
from modules.ai_assistant import AIAssistant
from ui.login_screen import LoginScreen
from core.auth_manager import AuthManage

class DevOSApplication:
    def __init__(self):
        self.error_handler = ErrorHandler()
        self.notifications = NotificationCenter()
        self.system_scanner = SystemScanner()
        self.knowledge_base = KnowledgeBase()
        self.module_loader = ModuleLoader()
        self.project_manager = ProjectManager(self)
        self.collab_server = CollaborationServer()
        self.profiler = PerformanceProfiler()
        self.hardware_manager = HardwareManager()
        self.ai_assistant = AIAssistant()
        self.auth_manager = AuthManager()
        
        # Setup logging
        self.setup_logging()
        
        # Register global error handler
        sys.excepthook = self.error_handler.global_exception_handler
        
    def setup_logging(self):
        logging.basicConfig(
            filename='devos.log',
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            filemode='w'
        )
        self.logger = logging.getLogger('DevOSCore')
        self.logger.info("Application initialized")
        
    def initialize(self):
        """Initialize all application components"""
        try:
            # Load system status
            self.system_status = self.system_scanner.full_scan()
            
            # Load knowledge base
            self.knowledge_base.load()
            
            # Load modules
            self.module_loader.load_all(self)
            
            # Initialize UI
            self.main_window = MainWindow(self)
            
            # Register notifications with UI
            self.notifications.register_ui(self.main_window.notification_bar)
            
            self.logger.info("All components initialized")
            return True
        except Exception as e:
            self.error_handler.handle(e, "Initialization")
            return False
            
    def run(self):
        """Main application entry point"""
        # Show login screen first
        self.login_screen = LoginScreen(self)
        self.login_screen.mainloop()

        # After login, proceed to main application
        if self.initialize():
            self.start_background_services()
            self.main_window.run()
        if not self.initialize():
            self.notifications.critical(
                "Initialization Failed",
                "Application failed to initialize. Check devos.log for details."
            )
            return
            
        # Start background services
        self.start_background_services()
        
        # Run main UI loop
        self.main_window.run()
        
    def start_background_services(self):
        """Start background monitoring services"""
        # System health monitor
        health_thread = threading.Thread(
            target=self.system_scanner.monitor_system_health,
            args=(self.notifications,),
            daemon=True
        )
        health_thread.start()
        
        # Knowledge base updater
        kb_thread = threading.Thread(
            target=self.knowledge_base.periodic_update,
            daemon=True
        )
        kb_thread.start()
        
    def repair_system(self, issue_id):
        """Attempt to repair a detected system issue"""
        return self.system_scanner.repair_issue(issue_id)
    
    def search_knowledge(self, query):
        """Search the knowledge base"""
        return self.knowledge_base.search(query)
    
    def get_resource(self, category, key):
        """Get a specific resource"""
        return self.knowledge_base.get_resource(category, key)
    
    def build_project(self, project_type, config):
        """Build a project"""
        return self.module_loader.get_builder(project_type).build(config)
