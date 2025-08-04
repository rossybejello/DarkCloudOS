import socket
import threading
import json
import time
import logging
from cryptography.fernet import Fernet

class CollaborationServer:
    def __init__(self, port=8888):
        self.port = port
        self.clients = {}
        self.running = False
        self.logger = logging.getLogger('CollabServer')
        self.encryption_key = Fernet.generate_key()
        self.cipher = Fernet(self.encryption_key)
        
    def start(self):
        """Start collaboration server"""
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(('0.0.0.0', self.port))
        self.server.listen(5)
        self.running = True
        
        self.logger.info(f"Collaboration server started on port {self.port}")
        threading.Thread(target=self.accept_clients, daemon=True).start()
        
    def stop(self):
        """Stop collaboration server"""
        self.running = False
        for client in self.clients.values():
            client.close()
        self.server.close()
        
    def accept_clients(self):
        """Accept incoming client connections"""
        while self.running:
            try:
                client, addr = self.server.accept()
                self.logger.info(f"New client connected: {addr}")
                
                # Send encryption key to client
                client.send(self.encryption_key)
                
                # Start client handler thread
                threading.Thread(
                    target=self.handle_client,
                    args=(client, addr),
                    daemon=True
                ).start()
            except OSError:
                break
                
    def handle_client(self, client, addr):
        """Handle communication with a client"""
        self.clients[addr] = client
        
        try:
            while self.running:
                data = client.recv(4096)
                if not data:
                    break
                    
                # Decrypt and process message
                decrypted = self.cipher.decrypt(data)
                message = json.loads(decrypted.decode())
                self.broadcast(message, exclude=addr)
        except (ConnectionResetError, json.JSONDecodeError):
            pass
        finally:
            del self.clients[addr]
            client.close()
            
    def broadcast(self, message, exclude=None):
        """Broadcast message to all clients except specified"""
        for addr, client in self.clients.items():
            if addr == exclude:
                continue
                
            try:
                encrypted = self.cipher.encrypt(json.dumps(message).encode())
                client.send(encrypted)
            except (ConnectionResetError, BrokenPipeError):
                del self.clients[addr]

class CollaborationClient:
    def __init__(self, host, port=8888):
        self.host = host
        self.port = port
        self.connected = False
        self.logger = logging.getLogger('CollabClient')
        self.cipher = None
        
    def connect(self):
        """Connect to collaboration server"""
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.host, self.port))
        self.connected = True
        
        # Receive encryption key
        self.encryption_key = self.client.recv(44)
        self.cipher = Fernet(self.encryption_key)
        
        self.logger.info(f"Connected to {self.host}:{self.port}")
        threading.Thread(target=self.receive_messages, daemon=True).start()
        return True
        
    def disconnect(self):
        """Disconnect from server"""
        self.connected = False
        self.client.close()
        
    def send(self, message):
        """Send a message to the server"""
        if not self.connected:
            return False
            
        try:
            encrypted = self.cipher.encrypt(json.dumps(message).encode())
            self.client.send(encrypted)
            return True
        except (ConnectionResetError, BrokenPipeError):
            self.connected = False
            return False
            
    def receive_messages(self):
        """Receive messages from server"""
        while self.connected:
            try:
                data = self.client.recv(4096)
                if not data:
                    break
                    
                # Decrypt and process message
                decrypted = self.cipher.decrypt(data)
                message = json.loads(decrypted.decode())
                self.on_message_received(message)
            except (ConnectionResetError, json.JSONDecodeError):
                self.connected = False
                break
                
    def on_message_received(self, message):
        """Handle received messages (to be overridden)"""
        pass