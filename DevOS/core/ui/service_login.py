import customtkinter as ctk
import webbrowser
import threading
from core.auth_manager import AuthManager
from core.notification import NotificationCenter
from core.error_handler import ErrorHandler

class ServiceLoginDialog(ctk.CTkToplevel):
    OAUTH_CONFIG = {
        "github": {
            "auth_url": "https://github.com/login/oauth/authorize",
            "token_url": "https://github.com/login/oauth/access_token",
            "scopes": "repo,user",
            "client_id": "YOUR_CLIENT_ID",  # Replace with actual client ID
            "client_secret": "YOUR_CLIENT_SECRET"  # Replace with actual secret
        },
        "dockerhub": {
            "auth_url": "https://hub.docker.com/v2/oauth2/authorize",
            "token_url": "https://hub.docker.com/v2/oauth2/token",
            "scopes": "repository:read,repository:write",
            "client_id": "YOUR_CLIENT_ID",
            "client_secret": "YOUR_CLIENT_SECRET"
        },
        # Add configurations for other services
    }
    
    def __init__(self, parent, service):
        super().__init__(parent)
        self.service = service
        self.auth = AuthManager()
        self.notifications = NotificationCenter()
        self.error_handler = ErrorHandler()
        
        self.title(f"Login to {service.capitalize()}")
        self.geometry("600x500")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        self.create_widgets()
        
    def create_widgets(self):
        # Service logo
        ctk.CTkLabel(self, text=f"{self.service.capitalize()} Login", font=("Arial", 20, "bold")).pack(pady=20)
        
        # Login methods
        method_frame = ctk.CTkFrame(self)
        method_frame.pack(fill="x", padx=50, pady=10)
        
        ctk.CTkLabel(method_frame, text="Login Method:", font=("Arial", 14)).pack(anchor="w", pady=5)
        
        self.method_var = ctk.StringVar(value="oauth")
        ctk.CTkRadioButton(
            method_frame, 
            text="OAuth (Recommended)", 
            variable=self.method_var, 
            value="oauth"
        ).pack(anchor="w", pady=5)
        
        ctk.CTkRadioButton(
            method_frame, 
            text="Personal Access Token", 
            variable=self.method_var, 
            value="pat"
        ).pack(anchor="w", pady=5)
        
        ctk.CTkRadioButton(
            method_frame, 
            text="Username/Password", 
            variable=self.method_var, 
            value="basic"
        ).pack(anchor="w", pady=5)
        
        # Credential input
        self.credential_frame = ctk.CTkFrame(self)
        self.credential_frame.pack(fill="x", padx=50, pady=10)
        self.update_credential_fields()
        
        # OAuth button
        self.oauth_button = ctk.CTkButton(
            self, 
            text=f"Authorize with {self.service.capitalize()}",
            command=self.start_oauth_flow
        )
        self.oauth_button.pack(pady=10)
        
        # Bind method change
        self.method_var.trace_add("write", self.on_method_change)
        
    def on_method_change(self, *args):
        """Update credential fields based on selected method"""
        self.update_credential_fields()
        
    def update_credential_fields(self):
        """Show appropriate credential fields"""
        # Clear existing fields
        for widget in self.credential_frame.winfo_children():
            widget.destroy()
            
        method = self.method_var.get()
        
        if method == "pat":
            # Personal Access Token fields
            ctk.CTkLabel(self.credential_frame, text="Access Token:").pack(anchor="w", pady=2)
            self.token_entry = ctk.CTkEntry(self.credential_frame, width=400)
            self.token_entry.pack(fill="x", pady=5)
            
            ctk.CTkButton(
                self.credential_frame, 
                text="Save Token", 
                command=self.save_token
            ).pack(pady=10)
            
            self.oauth_button.pack_forget()
            
        elif method == "basic":
            # Username/Password fields
            ctk.CTkLabel(self.credential_frame, text="Username:").pack(anchor="w", pady=2)
            self.username_entry = ctk.CTkEntry(self.credential_frame, width=400)
            self.username_entry.pack(fill="x", pady=5)
            
            ctk.CTkLabel(self.credential_frame, text="Password:").pack(anchor="w", pady=2)
            self.password_entry = ctk.CTkEntry(self.credential_frame, show="*", width=400)
            self.password_entry.pack(fill="x", pady=5)
            
            ctk.CTkButton(
                self.credential_frame, 
                text="Save Credentials", 
                command=self.save_basic_credentials
            ).pack(pady=10)
            
            self.oauth_button.pack_forget()
            
        else:  # OAuth
            self.oauth_button.pack(pady=10)
            
    def save_token(self):
        """Save personal access token"""
        token = self.token_entry.get()
        if not token:
            self.notifications.error("Error", "Please enter access token")
            return
            
        if self.auth.save_credentials(self.service, {"access_token": token}):
            self.notifications.success("Success", "Token saved successfully")
            self.destroy()
        else:
            self.notifications.error("Error", "Failed to save token")
            
    def save_basic_credentials(self):
        """Save username/password credentials"""
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            self.notifications.error("Error", "Please enter both username and password")
            return
            
        if self.auth.save_credentials(self.service, {
            "username": username,
            "password": password
        }):
            self.notifications.success("Success", "Credentials saved successfully")
            self.destroy()
        else:
            self.notifications.error("Error", "Failed to save credentials")
            
    def start_oauth_flow(self):
        """Start OAuth authentication flow"""
        if self.service not in self.OAUTH_CONFIG:
            self.notifications.error("Error", "OAuth not supported for this service")
            return
            
        config = self.OAUTH_CONFIG[self.service]
        
        # Generate state token for CSRF protection
        state = os.urandom(16).hex()
        
        # Open authorization URL in browser
        auth_url = (
            f"{config['auth_url']}?"
            f"client_id={config['client_id']}&"
            f"scope={config['scopes']}&"
            f"state={state}"
        )
        
        webbrowser.open(auth_url)
        
        # Show code input
        self.show_code_input(config, state)
        
    def show_code_input(self, config, state):
        """Show UI for entering OAuth code"""
        for widget in self.credential_frame.winfo_children():
            widget.destroy()
            
        ctk.CTkLabel(self.credential_frame, text="After authorization, enter the code you received:").pack(pady=10)
        
        self.code_entry = ctk.CTkEntry(self.credential_frame, width=300)
        self.code_entry.pack(pady=10)
        
        ctk.CTkButton(
            self.credential_frame, 
            text="Complete Authorization", 
            command=lambda: self.exchange_code(config, state)
        ).pack(pady=10)
        
    def exchange_code(self, config, state):
        """Exchange authorization code for access token"""
        code = self.code_entry.get()
        if not code:
            self.notifications.error("Error", "Please enter authorization code")
            return
            
        # This should be done in a background thread
        threading.Thread(
            target=self._exchange_code_thread,
            args=(config, code, state),
            daemon=True
        ).start()
        
    def _exchange_code_thread(self, config, code, state):
        """Thread for exchanging OAuth code (simplified)"""
        # In a real implementation, you would make HTTP requests here
        # This is a simplified example
        
        # Validate state
        # Make request to token endpoint
        # Extract access token
        
        # Simulate successful token exchange
        access_token = "simulated_access_token"
        refresh_token = "simulated_refresh_token"
        
        if self.auth.save_credentials(self.service, {
            "access_token": access_token,
            "refresh_token": refresh_token
        }):
            self.notifications.success("Success", "Login successful")
            self.destroy()
        else:
            self.notifications.error("Error", "Failed to complete authentication")