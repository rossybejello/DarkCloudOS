import tkinter as tk
import customtkinter as ctk
from .components import (
from ui.service_manager import ServiceManagerFrame
    NotificationBar,
    DashboardFrame,
    SystemHealthFrame,
    FrameworkFrame,
    CloudFrame,
    AIAssistantFrame,
    BlockchainFrame,
    KnowledgeBaseFrame,
    Tooltip
    ProjectExplorerFrame,
    CodeEditorFrame,
    CollaborationFrame,
    PerformanceFrame,
    HardwareFrame,
    AIAssistantFrame
)

class MainWindow:
    def __init__(self, application):
        self.app = application
        self.root = ctk.CTk()
        self.root.title("DevOS Master Toolkit")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)
        self.tab_project = self.tab_view.add("Projects")
        self.tab_editor = self.tab_view.add("Code Editor")
        self.tab_collab = self.tab_view.add("Collaboration")
        self.tab_performance = self.tab_view.add("Performance")
        self.tab_hardware = self.tab_view.add("Hardware")
        self.tab_ai = self.tab_view.add("AI Assistant")
        self.tab_services = self.tab_view.add("Services")

        # Initialize tab content
        self.project_frame = ProjectExplorerFrame(self.tab_project, self.app)
        self.project_frame.pack(fill="both", expand=True)

        self.editor_frame = CodeEditorFrame(self.tab_editor, self.app)
        self.editor_frame.pack(fill="both", expand=True)

        self.collab_frame = CollaborationFrame(self.tab_collab, self.app)
        self.collab_frame.pack(fill="both", expand=True)

        self.performance_frame = PerformanceFrame(self.tab_performance, self.app)
        self.performance_frame.pack(fill="both", expand=True)

        self.hardware_frame = HardwareFrame(self.tab_hardware, self.app)
        self.hardware_frame.pack(fill="both", expand=True)

        self.ai_frame = AIAssistantFrame(self.tab_ai, self.app)
        self.ai_frame.pack(fill="both", expand=True)

        self.services_frame = ServiceManagerFrame(self.tab_services, self.app)
        self.services_frame.pack(fill="both", expand=True)
        
        # Configure grid layout
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Create notification bar
        self.notification_bar = NotificationBar(self.root, self.app.notifications)
        self.notification_bar.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        
        # Create main tabs
        self.tab_view = ctk.CTkTabview(self.root)
        self.tab_view.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        # Add tabs
        self.tab_dashboard = self.tab_view.add("Dashboard")
        self.tab_system = self.tab_view.add("System Health")
        self.tab_frameworks = self.tab_view.add("Frameworks")
        self.tab_cloud = self.tab_view.add("Cloud")
        self.tab_ai = self.tab_view.add("AI Assistant")
        self.tab_blockchain = self.tab_view.add("Blockchain")
        self.tab_knowledge = self.tab_view.add("Knowledge Base")
        
        # Initialize tab content with tooltips
        self.dashboard_frame = DashboardFrame(self.tab_dashboard, self.app)
        self.dashboard_frame.pack(fill="both", expand=True)
        Tooltip.register(self.dashboard_frame, "System overview and quick actions")
        
        self.system_frame = SystemHealthFrame(self.tab_system, self.app)
        self.system_frame.pack(fill="both", expand=True)
        Tooltip.register(self.system_frame, "System diagnostics and repair tools")
        
        self.framework_frame = FrameworkFrame(self.tab_frameworks, self.app)
        self.framework_frame.pack(fill="both", expand=True)
        Tooltip.register(self.framework_frame, "Framework-specific development tools")
        
        self.cloud_frame = CloudFrame(self.tab_cloud, self.app)
        self.cloud_frame.pack(fill="both", expand=True)
        Tooltip.register(self.cloud_frame, "Cloud deployment and management")
        
        self.ai_frame = AIAssistantFrame(self.tab_ai, self.app)
        self.ai_frame.pack(fill="both", expand=True)
        Tooltip.register(self.ai_frame, "AI-assisted development tools")
        
        self.blockchain_frame = BlockchainFrame(self.tab_blockchain, self.app)
        self.blockchain_frame.pack(fill="both", expand=True)
        Tooltip.register(self.blockchain_frame, "Blockchain development tools")
        
        self.knowledge_frame = KnowledgeBaseFrame(self.tab_knowledge, self.app)
        self.knowledge_frame.pack(fill="both", expand=True)
        Tooltip.register(self.knowledge_frame, "Searchable knowledge base and resources")
        
    def run(self):
        self.root.mainloop()
        
    def show_notification(self, notification):
        """Display notification in UI"""
        self.notification_bar.add_notification(notification)
