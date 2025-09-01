import logging
import os
from datetime import datetime

def setup_logging():
    """Setup comprehensive logging configuration"""
    
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # File handler for detailed logs
    file_handler = logging.FileHandler(
        f'logs/bot_{datetime.now().strftime("%Y%m%d")}.log',
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    
    # Console handler for important messages
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    
    # Error file handler
    error_handler = logging.FileHandler(
        f'logs/errors_{datetime.now().strftime("%Y%m%d")}.log',
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    
    # Add handlers to root logger
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(error_handler)
    
    # Setup specific loggers
    telegram_logger = logging.getLogger('telegram')
    telegram_logger.setLevel(logging.WARNING)  # Reduce telegram library noise
    
    paypal_logger = logging.getLogger('paypalrestsdk')
    paypal_logger.setLevel(logging.WARNING)  # Reduce PayPal library noise
    
    # Log startup
    logging.info("Logging system initialized")
    logging.info(f"Log files: logs/bot_{datetime.now().strftime('%Y%m%d')}.log, logs/errors_{datetime.now().strftime('%Y%m%d')}.log")

def log_user_action(user_id: int, action: str, details: str = ""):
    """Log user actions for audit trail"""
    logging.info(f"USER_ACTION - User {user_id}: {action} - {details}")

def log_payment_event(payment_id: str, event: str, details: str = ""):
    """Log payment events for tracking"""
    logging.info(f"PAYMENT_EVENT - {payment_id}: {event} - {details}")

def log_error(error: Exception, context: str = ""):
    """Log errors with context"""
    logging.error(f"ERROR - {context}: {str(error)}", exc_info=True)