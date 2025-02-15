# utils/helpers.py

import logging

def log_error(error_message: str):
    """
    Logs an error message to the log file.
    """
    logging.error(error_message)

def log_info(info_message: str):
    """
    Logs an informational message to the log file.
    """
    logging.info(info_message)

def sanitize_input(input_str: str):
    """
    Sanitizes input data (e.g., remove unwanted characters, prevent injection attacks).
    """
    sanitized_str = input_str.strip().replace(";", "").replace("--", "")
    return sanitized_str
