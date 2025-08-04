import logging
import traceback
from core.notification import NotificationCenter, NotificationType
import sys

class ErrorHandler:
    def __init__(self):
        self.notifications = NotificationCenter()
        self.logger = logging.getLogger('ErrorHandler')
        
    def handle(self, error, context=None):
        """Handle an application error"""
        error_info = {
            'type': type(error).__name__,
            'message': str(error),
            'context': context,
            'traceback': traceback.format_exc()
        }
        
        self.logger.error(f"Error: {error_info}")
        self.notifications.error(
            "Application Error",
            f"{error_info['type']}: {error_info['message']}"
        )
        
        return error_info
        
    def global_exception_handler(self, exc_type, exc_value, exc_traceback):
        """Global exception handler"""
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
            
        self.handle(exc_value, "GlobalException")