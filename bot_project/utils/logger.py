import os
import logging
from logging.handlers import RotatingFileHandler

def setup_logging(log_file_path='logs/bot.log'):
    # Ensure the logs directory exists
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
    
    # Create logger
    logger = logging.getLogger('OddsBot')
    logger.setLevel(logging.INFO)
    
    # Create file handler
    file_handler = RotatingFileHandler(
        log_file_path, 
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'  # Ensure file handler uses UTF-8
    )
    file_handler.setLevel(logging.INFO)
    
    # Create console handler with UTF-8 encoding
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger