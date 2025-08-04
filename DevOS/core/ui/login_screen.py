import customtkinter as ctk
from core.auth_manager import AuthManager
from core.notification import NotificationCenter
from core.error_handler import ErrorHandler

class LoginScreen(ctk.CTk):
    def __init__(self, application):
        super().__init__()
        self.app = application
        self.auth = AuthManager()
        self.notifications = NotificationCenter()
        self.error_handler = ErrorHandler()
        
        self.title("DevOS Toolkit - Login")
        self.geometry("500x400")
        self.resizable(False, False)
        
        self.create_widgets()
        self.check_existing_master()
        
    def check_existing_master(self):
        """Check if master password exists"""
        if os.path.exists("auth/master.salt"):
            self.title_label.configure(text="Enter Master Password")
            self.confirm_password_entry.grid_remove()
            self.set_password_button.grid_remove()
            self.login_button.grid()
        else:
            self.title_label.configure(text="Set Master Password")
            self.confirm_password_entry.grid()
            self.set_password_button.grid()
            self.login_button.grid_remove()
        
    def create_widgets(self):
        # Title
        self.title_label = ctk.CTkLabel(self, text="", font=("Arial", 20, "bold"))
        self.title_label.pack(pady=20)
        
        # Password frame
        password_frame = ctk.CTkFrame(self)
        password_frame.pack(fill="x", padx=50, pady=10)
        
        ctk.CTkLabel(password_frame, text="Password:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.password_entry = ctk.CTkEntry(password_frame, show="*", width=300)
        self.password_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Confirm password frame
        confirm_frame = ctk.CTkFrame(self)
        confirm_frame.pack(fill="x", padx=50, pady=10)
        
        ctk.CTkLabel(confirm_frame, text="Confirm Password:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.confirm_password_entry = ctk.CTkEntry(confirm_frame, show="*", width=300)
        self.confirm_password_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Buttons
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(pady=20)
        
        self.set_password_button = ctk.CTkButton(
            button_frame, 
            text="Set Master Password", 
            command=self.set_master_password
        )
        self.set_password_button.grid(row=0, column=0, padx=10)
        
        self.login_button = ctk.CTkButton(
            button_frame, 
            text="Login", 
            command=self.login
        )
        
        self.forgot_button = ctk.CTkButton(
            button_frame, 
            text="Reset Password", 
            command=self.reset_password,
            fg_color="transparent",
            border_width=1
        )
        self.forgot_button.grid(row=0, column=1, padx=10)
        
        # Service login status
        self.status_frame = ctk.CTkFrame(self)
        self.status_frame.pack(fill="x", padx=50, pady=20)
        
        ctk.CTkLabel(self.status_frame, text="Service Login Status", font=("Arial", 14, "bold")).pack(anchor="w", pady=5)
        
        self.status_labels = {}
        for service in self.auth.SUPPORTED_SERVICES:
            frame = ctk.CTkFrame(self.status_frame)
            frame.pack(fill="x", pady=2)
            
            ctk.CTkLabel(frame, text=f"{service.capitalize()}:", width=100).pack(side="left")
            label = ctk.CTkLabel(frame, text="Not logged in", text_color="red")
            label.pack(side="left")
            self.status_labels[service] = label
            
        # Update status
        self.update_service_status()
        
    def update_service_status(self):
        """Update service login status indicators"""
        for service in self.auth.SUPPORTED_SERVICES:
            if self.auth.get_service_status(service):
                self.status_labels[service].configure(text="Logged in", text_color="green")
            else:
                self.status_labels[service].configure(text="Not logged in", text_color="red")
    
    def set_master_password(self):
        """Set the master password"""
        password = self.password_entry.get()
        confirm = self.confirm_password_entry.get()
        
        if not password or len(password) < 8:
            self.notifications.error("Password Error", "Password must be at least 8 characters")
            return
            
        if password != confirm:
            self.notifications.error("Password Error", "Passwords do not match")
            return
            
        if self.auth.set_master_password(password):
            self.notifications.success("Success", "Master password set successfully")
            self.destroy()
            self.app.run()
        else:
            self.notifications.error("Error", "Failed to set master password")
    
    def login(self):
        """Login with master password"""
        password = self.password_entry.get()
        
        if not password:
            self.notifications.error("Password Error", "Please enter password")
            return
            
        if self.auth.load_master_key(password):
            self.notifications.success("Success", "Login successful")
            self.destroy()
            self.app.run()
        else:
            self.notifications.error("Error", "Invalid password")
            
    def reset_password(self):
        """Reset master password (will delete all credentials)"""
        # Warning - this will delete all saved credentials
        import shutil
        if os.path.exists("auth"):
            shutil.rmtree("auth")
        self.notifications.warning("Password Reset", "All credentials have been deleted")
        self.check_existing_master()