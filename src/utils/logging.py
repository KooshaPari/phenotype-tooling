"""
Logging configuration for the SWE agent.
"""
import logging
import sys
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler
import json
from datetime import datetime

# Create the logs directory if it doesn't exist
LOGS_DIR = Path(__file__).parent.parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Configure the root logger
def configure_logging(level=logging.INFO):
    """
    Configure the root logger.
    
    Args:
        level: Logging level.
    """
    # Create a formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create a console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Create a file handler
    file_handler = RotatingFileHandler(
        LOGS_DIR / "swe_agent.log",
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    
    # Configure the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    return root_logger

# Create a logger for the SWE agent
logger = configure_logging()

class RequestResponseLogger:
    """
    Logger for API requests and responses.
    """
    
    def __init__(self):
        """
        Initialize the request/response logger.
        """
        self.log_file = LOGS_DIR / "api.log"
    
    def log_request(self, request_id: str, endpoint: str, method: str, data: dict = None):
        """
        Log an API request.
        
        Args:
            request_id: Request ID.
            endpoint: API endpoint.
            method: HTTP method.
            data: Request data.
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "request_id": request_id,
            "type": "request",
            "endpoint": endpoint,
            "method": method,
            "data": data
        }
        self._write_log(log_entry)
    
    def log_response(self, request_id: str, status_code: int, data: dict = None):
        """
        Log an API response.
        
        Args:
            request_id: Request ID.
            status_code: HTTP status code.
            data: Response data.
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "request_id": request_id,
            "type": "response",
            "status_code": status_code,
            "data": data
        }
        self._write_log(log_entry)
    
    def _write_log(self, log_entry: dict):
        """
        Write a log entry to the log file.
        
        Args:
            log_entry: Log entry.
        """
        with open(self.log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

# Create a request/response logger
request_logger = RequestResponseLogger()
