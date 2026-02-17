import logging
import json
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

class JsonFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    def format(self, record):
        log_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "funcName": record.funcName,
            "lineNo": record.lineno,
        }
        
        # Add extra fields if present
        if hasattr(record, "metadata"):
            log_record["metadata"] = record.metadata
            
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_record)

def setup_logger(name, log_file="logs/app.jsonl", level=logging.INFO):
    """Setup and return a configured logger."""
    
    # Ensure logs directory exists
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid duplicate handlers if setup is called multiple times
    if logger.handlers:
        return logger
        
    # Rotating File Handler (max 5MB, keep 5 backups)
    handler = RotatingFileHandler(
        log_file, maxBytes=5*1024*1024, backupCount=5, encoding='utf-8'
    )
    
    formatter = JsonFormatter()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    # Also log to console for development (optional)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    # logger.addHandler(console_handler) # Uncomment if you want console logs too
    
    return logger

# Example usage
if __name__ == "__main__":
    log = setup_logger("test_logger")
    log.info("Test message", extra={"metadata": {"user_id": 123, "action": "login"}})
    try:
        1 / 0
    except ZeroDivisionError:
        log.error("Math error", exc_info=True, extra={"metadata": {"context": "division"}})
