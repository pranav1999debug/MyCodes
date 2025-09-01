import logging
import traceback
from typing import Callable, Any
from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes

def handle_errors(func: Callable) -> Callable:
    """Decorator to handle errors in bot functions"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logging.error(f"Error in {func.__name__}: {str(e)}")
            logging.error(traceback.format_exc())
            
            # Try to send error message to user if possible
            try:
                update = None
                for arg in args:
                    if isinstance(arg, Update):
                        update = arg
                        break
                
                if update and update.effective_chat:
                    error_message = """
❌ <b>An error occurred</b>

We're sorry, but something went wrong. Please try again later or contact support if the problem persists.

<b>Error ID:</b> <code>{error_id}</code>
                    """.format(error_id=hash(str(e)) % 100000)
                    
                    await update.effective_chat.send_message(
                        error_message,
                        parse_mode='HTML'
                    )
            except Exception as send_error:
                logging.error(f"Failed to send error message: {send_error}")
            
            return None
    
    return wrapper

class BotError(Exception):
    """Custom exception for bot-specific errors"""
    pass

class PaymentError(BotError):
    """Payment-related errors"""
    pass

class DatabaseError(BotError):
    """Database-related errors"""
    pass

class ValidationError(BotError):
    """Input validation errors"""
    pass

def validate_user_input(text: str, max_length: int = 1000) -> bool:
    """Validate user input"""
    if not text or not isinstance(text, str):
        return False
    
    if len(text) > max_length:
        return False
    
    # Check for potentially harmful content
    dangerous_patterns = [
        '<script', 'javascript:', 'data:', 'vbscript:',
        'onload=', 'onerror=', 'onclick='
    ]
    
    text_lower = text.lower()
    for pattern in dangerous_patterns:
        if pattern in text_lower:
            return False
    
    return True

def safe_int(value: Any, default: int = 0) -> int:
    """Safely convert value to integer"""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def safe_float(value: Any, default: float = 0.0) -> float:
    """Safely convert value to float"""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage"""
    import re
    # Remove or replace dangerous characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove multiple underscores
    filename = re.sub(r'_+', '_', filename)
    # Remove leading/trailing underscores
    filename = filename.strip('_')
    return filename

def rate_limit_check(user_id: int, action: str, limit: int = 10, window: int = 60) -> bool:
    """Simple rate limiting check"""
    import time
    from collections import defaultdict
    
    # In-memory rate limiting (in production, use Redis or database)
    if not hasattr(rate_limit_check, 'user_actions'):
        rate_limit_check.user_actions = defaultdict(list)
    
    current_time = time.time()
    user_actions = rate_limit_check.user_actions[user_id]
    
    # Remove old actions outside the window
    user_actions[:] = [action_time for action_time in user_actions if current_time - action_time < window]
    
    # Check if user has exceeded limit
    if len(user_actions) >= limit:
        return False
    
    # Add current action
    user_actions.append(current_time)
    return True

def log_error(error: Exception, context: str = ""):
    """Log errors with context"""
    logging.error(f"ERROR - {context}: {str(error)}", exc_info=True)

def log_security_event(user_id: int, event_type: str, details: str = ""):
    """Log security-related events"""
    logging.warning(f"SECURITY_EVENT - User {user_id} - {event_type}: {details}")

def check_admin_permissions(user_id: int) -> bool:
    """Check if user has admin permissions"""
    # Add your admin user IDs here
    admin_ids = [
        # Add your Telegram user ID here
        # Example: 123456789
    ]
    return user_id in admin_ids