import yaml
import logging
from pathlib import Path

class AIOrchestrator:
    def __init__(self, config_path):
        self.config = self._load_config(config_path)
        self.oblix_router = None
        self.wren_engine = None
        self.mcp_registry = None
        self._initialize_components()
        
    def _load_config(self, config_path):
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def _initialize_components(self):
        # Initialize Oblix if enabled
        if self.config.get('oblix', {}).get('enabled', False):
            self._initialize_oblix()
            
        # Initialize Wren Engine if enabled
        if self.config.get('wren', {}).get('enabled', False):
            self._initialize_wren()
            
        # Initialize MCP Auto Register if enabled
        if self.config.get('mcp_auto_register', {}).get('enabled', False):
            self._initialize_mcp_registry()
    
    def _initialize_oblix(self):
        # Import and initialize Oblix router
        logging.info("Initializing Oblix router")
        from .oblix_router import OblixRouter
        self.oblix_router = OblixRouter(self.config['oblix'])
        
    def _initialize_wren(self):
        # Import and initialize Wren Engine
        logging.info("Initializing Wren Engine")
        from .wren_integration import WrenEngineIntegration
        self.wren_engine = WrenEngineIntegration(self.config['wren'])
        
    def _initialize_mcp_registry(self):
        # Import and initialize MCP Auto Register
        logging.info("Initializing MCP Auto Register")
        from .mcp_registry import MCPRegistry
        self.mcp_registry = MCPRegistry(self.config['mcp_auto_register'])
    
    def process_request(self, request):
        """
        Process an AI request through the orchestration pipeline
        
        Args:
            request: Dict containing request parameters
            
        Returns:
            Dict containing the response
        """
        # Determine routing strategy
        if self.wren_engine:
            # Use Wren Engine to select the best model
            model = self.wren_engine.select_model(request)
            request['model'] = model
            
        # Route to appropriate execution environment
        if self.oblix_router:
            response = self.oblix_router.route_request(request)
        else:
            # Fallback to direct execution
            response = self._direct_execution(request)
            
        return response
    
    def _direct_execution(self, request):
        # Fallback execution method
        # TODO: Implement direct model calling
        return {"source": "direct", "model": request.get('model', 'unknown'), "text": "This is a placeholder response from direct execution"}
    
    def get_available_plugins(self):
        """Return list of available MCP plugins"""
        if self.mcp_registry:
            return self.mcp_registry.get_available_plugins()
        return []
