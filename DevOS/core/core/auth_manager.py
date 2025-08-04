import os
import json
import keyring
import hashlib
import base64
import logging
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from core.error_handler import ErrorHandler

class AuthManager:
    SUPPORTED_SERVICES = [
        "github", "dockerhub", "aws", "azure", "gcp", 
        "gitlab", "bitbucket", "npm", "pypi"
    ]
    
    def __init__(self):
        self.error_handler = ErrorHandler()
        self.logger = logging.getLogger('AuthManager')
        self.credentials_file = "auth/credentials.json"
        self.master_key = None
        self.ensure_auth_dir()
        
    def ensure_auth_dir(self):
        """Create auth directory if needed"""
        os.makedirs("auth", exist_ok=True)
        
    def set_master_password(self, password):
        """Set and derive master encryption key"""
        try:
            salt = os.urandom(16)
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=480000,
            )
            self.master_key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            
            # Save salt for later derivation
            with open("auth/master.salt", "wb") as f:
                f.write(salt)
                
            return True
        except Exception as e:
            self.error_handler.handle(e, "set_master_password")
            return False
            
    def load_master_key(self, password):
        """Load master key using stored salt"""
        try:
            with open("auth/master.salt", "rb") as f:
                salt = f.read()
                
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=480000,
            )
            self.master_key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            return True
        except Exception as e:
            self.error_handler.handle(e, "load_master_key")
            return False
            
    def encrypt_data(self, data):
        """Encrypt data using master key"""
        cipher = Fernet(self.master_key)
        return cipher.encrypt(data.encode()).decode()
    
    def decrypt_data(self, encrypted_data):
        """Decrypt data using master key"""
        cipher = Fernet(self.master_key)
        return cipher.decrypt(encrypted_data.encode()).decode()
    
    def save_credentials(self, service, credentials):
        """Save credentials for a service"""
        try:
            # Load existing credentials
            all_creds = {}
            if os.path.exists(self.credentials_file):
                with open(self.credentials_file, "r") as f:
                    all_creds = json.load(f)
            
            # Encrypt sensitive data
            protected_creds = {}
            for key, value in credentials.items():
                if "token" in key or "secret" in key or "password" in key:
                    protected_creds[key] = self.encrypt_data(value)
                else:
                    protected_creds[key] = value
                    
            # Store in keyring for sensitive data
            if "access_token" in protected_creds:
                keyring.set_password(
                    "devos_toolkit", 
                    f"{service}_access_token", 
                    protected_creds.pop("access_token")
                )
                
            if "refresh_token" in protected_creds:
                keyring.set_password(
                    "devos_toolkit", 
                    f"{service}_refresh_token", 
                    protected_creds.pop("refresh_token")
                )
            
            # Save remaining credentials to file
            all_creds[service] = protected_creds
            with open(self.credentials_file, "w") as f:
                json.dump(all_creds, f, indent=2)
                
            return True
        except Exception as e:
            self.error_handler.handle(e, "save_credentials")
            return False
            
    def get_credentials(self, service):
        """Get credentials for a service"""
        try:
            # Load from file
            if not os.path.exists(self.credentials_file):
                return None
                
            with open(self.credentials_file, "r") as f:
                all_creds = json.load(f)
                
            if service not in all_creds:
                return None
                
            creds = all_creds[service]
            
            # Retrieve tokens from keyring
            access_token = keyring.get_password("devos_toolkit", f"{service}_access_token")
            refresh_token = keyring.get_password("devos_toolkit", f"{service}_refresh_token")
            
            if access_token:
                creds["access_token"] = access_token
            if refresh_token:
                creds["refresh_token"] = refresh_token
                
            # Decrypt sensitive data
            decrypted_creds = {}
            for key, value in creds.items():
                if isinstance(value, str) and ("token" in key or "secret" in key or "password" in key):
                    decrypted_creds[key] = self.decrypt_data(value)
                else:
                    decrypted_creds[key] = value
                    
            return decrypted_creds
        except Exception as e:
            self.error_handler.handle(e, "get_credentials")
            return None
            
    def delete_credentials(self, service):
        """Delete credentials for a service"""
        try:
            # Load existing credentials
            if not os.path.exists(self.credentials_file):
                return False
                
            with open(self.credentials_file, "r") as f:
                all_creds = json.load(f)
                
            if service not in all_creds:
                return False
                
            # Remove from keyring
            keyring.delete_password("devos_toolkit", f"{service}_access_token")
            keyring.delete_password("devos_toolkit", f"{service}_refresh_token")
            
            # Remove from file
            del all_creds[service]
            with open(self.credentials_file, "w") as f:
                json.dump(all_creds, f, indent=2)
                
            return True
        except Exception as e:
            self.error_handler.handle(e, "delete_credentials")
            return False
            
    def get_service_status(self, service):
        """Check if credentials exist for a service"""
        return self.get_credentials(service) is not None