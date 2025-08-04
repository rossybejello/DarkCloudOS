import importlib
import pkgutil
import logging
from .frameworks import FrameworkManager
from .cloud import CloudManager
from .blockchain import BlockchainManager
from .ai import AIManager

class ModuleLoader:
    def __init__(self):
        self.logger = logging.getLogger('ModuleLoader')
        self.modules = {}
        
    def load_all(self, application):
        """Load all available modules"""
        self.logger.info("Loading modules")
        
        # Load framework manager
        self.framework_manager = FrameworkManager(application)
        self.modules['frameworks'] = self.framework_manager
        
        # Load cloud manager
        self.cloud_manager = CloudManager(application)
        self.modules['cloud'] = self.cloud_manager
        
        # Load blockchain manager
        self.blockchain_manager = BlockchainManager(application)
        self.modules['blockchain'] = self.blockchain_manager
        
        # Load AI manager
        self.ai_manager = AIManager(application)
        self.modules['ai'] = self.ai_manager
        
        self.logger.info("All modules loaded")
        
    def get_builder(self, builder_type):
        """Get a builder for a specific type"""
        if builder_type == 'framework':
            return self.framework_manager
        elif builder_type == 'cloud':
            return self.cloud_manager
        elif builder_type == 'blockchain':
            return self.blockchain_manager
        return None