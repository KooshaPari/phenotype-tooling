import logging
import os
import json
import time
import threading
import requests
from pathlib import Path

class MCPRegistry:
    """
    Integration with MCP Auto Register for plugin discovery and management
    """
    
    def __init__(self, config):
        self.config = config
        self.plugins = {}
        self.plugins_directory = config.get('plugins_directory', './plugins')
        self.remote_registry_url = config.get('remote_registry_url')
        self.discovery_interval = config.get('discovery_interval', 60)
        self.health_check_interval = config.get('health_check_interval', 300)
        
        # Create plugins directory if it doesn't exist
        os.makedirs(self.plugins_directory, exist_ok=True)
        
        # Start background threads
        self._start_background_tasks()
        
    def _start_background_tasks(self):
        """Start background tasks for discovery and health checks"""
        # Start plugin discovery thread
        discovery_thread = threading.Thread(
            target=self._discovery_loop,
            daemon=True
        )
        discovery_thread.start()
        
        # Start health check thread
        health_thread = threading.Thread(
            target=self._health_check_loop,
            daemon=True
        )
        health_thread.start()
        
    def _discovery_loop(self):
        """Background loop for plugin discovery"""
        while True:
            try:
                self._discover_local_plugins()
                self._discover_remote_plugins()
            except Exception as e:
                logging.error(f"Error in plugin discovery: {str(e)}")
            
            time.sleep(self.discovery_interval)
            
    def _health_check_loop(self):
        """Background loop for plugin health checks"""
        while True:
            try:
                self._check_plugin_health()
            except Exception as e:
                logging.error(f"Error in plugin health check: {str(e)}")
            
            time.sleep(self.health_check_interval)
            
    def _discover_local_plugins(self):
        """Discover plugins in the local plugins directory"""
        plugins_path = Path(self.plugins_directory)
        for plugin_file in plugins_path.glob("*.json"):
            try:
                with open(plugin_file, 'r') as f:
                    plugin_data = json.load(f)
                    
                plugin_id = plugin_data.get('id') or plugin_file.stem
                self.plugins[plugin_id] = {
                    **plugin_data,
                    'source': 'local',
                    'last_seen': time.time(),
                    'status': 'discovered'
                }
                logging.info(f"Discovered local plugin: {plugin_id}")
            except Exception as e:
                logging.error(f"Error loading plugin {plugin_file}: {str(e)}")
                
    def _discover_remote_plugins(self):
        """Discover plugins from remote registry"""
        if not self.remote_registry_url:
            return
            
        try:
            response = requests.get(f"{self.remote_registry_url}/plugins")
            if response.status_code == 200:
                remote_plugins = response.json().get('plugins', [])
                for plugin_data in remote_plugins:
                    plugin_id = plugin_data.get('id')
                    if plugin_id:
                        self.plugins[plugin_id] = {
                            **plugin_data,
                            'source': 'remote',
                            'last_seen': time.time(),
                            'status': 'discovered'
                        }
                        logging.info(f"Discovered remote plugin: {plugin_id}")
        except Exception as e:
            logging.error(f"Error discovering remote plugins: {str(e)}")
            
    def _check_plugin_health(self):
        """Check health of all registered plugins"""
        for plugin_id, plugin in list(self.plugins.items()):
            try:
                if plugin.get('source') == 'local':
                    # For local plugins, check if file still exists
                    plugin_path = Path(self.plugins_directory) / f"{plugin_id}.json"
                    if plugin_path.exists():
                        plugin['status'] = 'healthy'
                        plugin['last_seen'] = time.time()
                    else:
                        plugin['status'] = 'missing'
                        
                elif plugin.get('source') == 'remote' and plugin.get('health_endpoint'):
                    # For remote plugins, check health endpoint
                    response = requests.get(plugin['health_endpoint'], timeout=5)
                    if response.status_code == 200:
                        plugin['status'] = 'healthy'
                        plugin['last_seen'] = time.time()
                    else:
                        plugin['status'] = 'unhealthy'
                        
            except Exception as e:
                logging.warning(f"Health check failed for plugin {plugin_id}: {str(e)}")
                plugin['status'] = 'unhealthy'
                
            # Remove plugins not seen for a long time
            if time.time() - plugin.get('last_seen', 0) > 3600:  # 1 hour
                logging.info(f"Removing stale plugin: {plugin_id}")
                self.plugins.pop(plugin_id, None)
                
    def get_available_plugins(self):
        """Get list of available plugins"""
        return [
            {
                'id': plugin_id,
                'name': plugin.get('name', plugin_id),
                'description': plugin.get('description', ''),
                'capabilities': plugin.get('capabilities', []),
                'status': plugin.get('status', 'unknown'),
                'source': plugin.get('source', 'unknown')
            }
            for plugin_id, plugin in self.plugins.items()
            if plugin.get('status') in ['healthy', 'discovered']
        ]
        
    def register_plugin(self, plugin_data):
        """Register a new plugin"""
        plugin_id = plugin_data.get('id')
        if not plugin_id:
            raise ValueError("Plugin ID is required")
            
        # Save to local plugins directory
        plugin_path = Path(self.plugins_directory) / f"{plugin_id}.json"
        with open(plugin_path, 'w') as f:
            json.dump(plugin_data, f, indent=2)
            
        # Add to in-memory registry
        self.plugins[plugin_id] = {
            **plugin_data,
            'source': 'local',
            'last_seen': time.time(),
            'status': 'discovered'
        }
        
        logging.info(f"Registered new plugin: {plugin_id}")
        return plugin_id
