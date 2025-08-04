import customtkinter as ctk
from ui.service_login import ServiceLoginDialog
from core.auth_manager import AuthManager
from core.notification import NotificationCenter

class ServiceManagerFrame(ctk.CTkFrame):
    def __init__(self, parent, application):
        super().__init__(parent)
        self.app = application
        self.auth = application.auth_manager
        self.notifications = application.notifications
        self.create_widgets()
        
    def create_widgets(self):
        # Title
        ctk.CTkLabel(self, text="Service Credentials", font=("Arial", 16, "bold")).pack(pady=10)
        
        # Services grid
        grid_frame = ctk.CTkFrame(self)
        grid_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create 3 columns
        grid_frame.columnconfigure(0, weight=1)
        grid_frame.columnconfigure(1, weight=1)
        grid_frame.columnconfigure(2, weight=1)
        
        row, col = 0, 0
        for service in self.auth.SUPPORTED_SERVICES:
            service_frame = ctk.CTkFrame(grid_frame)
            service_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            
            # Service icon and name
            ctk.CTkLabel(service_frame, text=service.capitalize(), font=("Arial", 14)).pack(pady=5)
            
            # Status indicator
            status_label = ctk.CTkLabel(service_frame, text="")
            status_label.pack(pady=5)
            self.update_service_status(service, status_label)
            
            # Action buttons
            btn_frame = ctk.CTkFrame(service_frame)
            btn_frame.pack(pady=5)
            
            if self.auth.get_service_status(service):
                ctk.CTkButton(
                    btn_frame, 
                    text="Logout", 
                    command=lambda s=service: self.logout_service(s),
                    width=80
                ).pack(side="left", padx=2)
            else:
                ctk.CTkButton(
                    btn_frame, 
                    text="Login", 
                    command=lambda s=service: self.login_service(s),
                    width=80
                ).pack(side="left", padx=2)
                
            # Move to next cell
            col += 1
            if col > 2:
                col = 0
                row += 1
                
    def update_service_status(self, service, label):
        """Update status label for service"""
        if self.auth.get_service_status(service):
            label.configure(text="Logged in", text_color="green")
        else:
            label.configure(text="Not logged in", text_color="red")
            
    def login_service(self, service):
        """Open login dialog for service"""
        dialog = ServiceLoginDialog(self, service)
        
    def logout_service(self, service):
        """Logout from service"""
        if self.auth.delete_credentials(service):
            self.notifications.success("Success", f"Logged out from {service}")
            # Refresh UI
            self.destroy()
            self.create_widgets()
        else:
            self.notifications.error("Error", f"Failed to logout from {service}")