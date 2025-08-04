import customtkinter as ctk
from core.notification import NotificationType
import time

class NotificationBar(ctk.CTkFrame):
    def __init__(self, parent, notification_center):
        super().__init__(parent)
        self.notification_center = notification_center
        self.notifications = []
        self.configure(height=30)
        self.create_widgets()
        
    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.label = ctk.CTkLabel(self, text="", anchor="w")
        self.label.grid(row=0, column=0, sticky="ew", padx=10)
        
        # Status indicators
        self.status_frame = ctk.CTkFrame(self)
        self.status_frame.grid(row=0, column=1, sticky="e")
        
        self.cpu_label = ctk.CTkLabel(self.status_frame, text="CPU: --%")
        self.cpu_label.pack(side="left", padx=5)
        
        self.mem_label = ctk.CTkLabel(self.status_frame, text="MEM: --%")
        self.mem_label.pack(side="left", padx=5)
        
        self.update_status()
        
    def update_status(self):
        # In a real implementation, you would get actual system metrics
        self.cpu_label.configure(text="CPU: 42%")
        self.mem_label.configure(text="MEM: 65%")
        self.after(5000, self.update_status)
        
    def add_notification(self, notification):
        """Add a notification to the bar"""
        # For simplicity, we'll just show the latest notification
        # In a full implementation, you'd manage multiple notifications
        
        # Set text and color based on type
        self.label.configure(text=f"{notification.title}: {notification.message}")
        
        color_map = {
            NotificationType.INFO: ("black", "lightblue"),
            NotificationType.SUCCESS: ("black", "lightgreen"),
            NotificationType.WARNING: ("black", "yellow"),
            NotificationType.ERROR: ("white", "orange"),
            NotificationType.CRITICAL: ("white", "red")
        }
        
        fg_color, bg_color = color_map.get(notification.type, ("black", "lightgray"))
        self.label.configure(text_color=fg_color, fg_color=bg_color)
        
        # Schedule removal
        if notification.timeout > 0:
            self.after(notification.timeout * 1000, self.clear_notification)
    
    def clear_notification(self):
        """Clear the current notification"""
        self.label.configure(text="", fg_color="transparent")