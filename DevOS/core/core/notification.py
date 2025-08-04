import logging
import time
from enum import Enum
import threading
import queue

class NotificationType(Enum):
    INFO = 1
    SUCCESS = 2
    WARNING = 3
    ERROR = 4
    CRITICAL = 5

class Notification:
    def __init__(self, title, message, ntype, timestamp=None, timeout=5):
        self.title = title
        self.message = message
        self.type = ntype
        self.timestamp = timestamp or time.time()
        self.timeout = timeout
        self.expired = False
        
    def check_expired(self):
        if time.time() - self.timestamp > self.timeout:
            self.expired = True
        return self.expired

class NotificationCenter:
    def __init__(self):
        self.logger = logging.getLogger('Notifications')
        self.ui_handler = None
        self.notification_queue = queue.Queue()
        self.active_notifications = []
        self.listener_thread = threading.Thread(target=self._process_queue, daemon=True)
        self.listener_thread.start()
        
    def register_ui(self, ui_handler):
        """Register UI notification manager"""
        self.ui_handler = ui_handler
        
    def _process_queue(self):
        """Process notification queue in background"""
        while True:
            notification = self.notification_queue.get()
            if notification is None:
                break
                
            self.active_notifications.append(notification)
            self._dispatch(notification)
            
    def _dispatch(self, notification):
        """Dispatch notification to all handlers"""
        # Log the notification
        self.logger.log(
            self._log_level(notification.type),
            f"{notification.title}: {notification.message}"
        )
            
        # Send to UI
        if self.ui_handler:
            self.ui_handler.show_notification(notification)
            
    def send(self, title, message, ntype=NotificationType.INFO, timeout=5):
        """Send a notification"""
        notification = Notification(title, message, ntype, timeout=timeout)
        self.notification_queue.put(notification)
        return notification
        
    def _log_level(self, ntype):
        """Map notification type to log level"""
        return {
            NotificationType.INFO: logging.INFO,
            NotificationType.SUCCESS: logging.INFO,
            NotificationType.WARNING: logging.WARNING,
            NotificationType.ERROR: logging.ERROR,
            NotificationType.CRITICAL: logging.CRITICAL
        }[ntype]
        
    # Convenience methods
    def info(self, title, message, timeout=3):
        self.send(title, message, NotificationType.INFO, timeout)
        
    def success(self, title, message, timeout=3):
        self.send(title, message, NotificationType.SUCCESS, timeout)
        
    def warning(self, title, message, timeout=5):
        self.send(title, message, NotificationType.WARNING, timeout)
        
    def error(self, title, message, timeout=8):
        self.send(title, message, NotificationType.ERROR, timeout)
        
    def critical(self, title, message, timeout=0):
        self.send(title, message, NotificationType.CRITICAL, timeout)
        
    def cleanup_expired(self):
        """Clean up expired notifications"""
        self.active_notifications = [
            n for n in self.active_notifications if not n.check_expired()
        ]