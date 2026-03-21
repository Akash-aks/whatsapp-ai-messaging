"""
Helper utility functions
Miscellaneous utility functions used across the application
"""

import re
from datetime import datetime
from typing import Optional

def format_phone_number(phone: str, country_code: str = "91") -> Optional[str]:
    """
    Format phone number with country code
    
    Args:
        phone: Phone number string
        country_code: Country code (default: 91 for India)
        
    Returns:
        Formatted phone number or None if invalid
    """
    if not phone:
        return None
    
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', str(phone))
    
    # Check minimum length
    if len(digits) < 10:
        return None
    
    # Add country code if not present
    if not digits.startswith(country_code) and len(digits) == 10:
        digits = country_code + digits
    
    return digits

def truncate_string(text: str, length: int = 50, suffix: str = "...") -> str:
    """
    Truncate string to specified length
    
    Args:
        text: Input string
        length: Maximum length
        suffix: Suffix to add when truncated
        
    Returns:
        Truncated string
    """
    if len(text) <= length:
        return text
    return text[:length - len(suffix)] + suffix

def format_timestamp(dt: datetime = None) -> str:
    """
    Format datetime as readable string
    
    Args:
        dt: Datetime object (default: now)
        
    Returns:
        Formatted timestamp string
    """
    if dt is None:
        dt = datetime.now()
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def sanitize_filename(filename: str) -> str:
    """
    Remove invalid characters from filename
    
    Args:
        filename: Input filename
        
    Returns:
        Sanitized filename
    """
    # Remove invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Replace spaces with underscores
    sanitized = sanitized.replace(' ', '_')
    return sanitized

def estimate_time(items: int, seconds_per_item: float) -> str:
    """
    Estimate time required for processing
    
    Args:
        items: Number of items to process
        seconds_per_item: Average time per item
        
    Returns:
        Human-readable time estimate
    """
    total_seconds = items * seconds_per_item
    
    if total_seconds < 60:
        return f"{int(total_seconds)} seconds"
    elif total_seconds < 3600:
        minutes = int(total_seconds / 60)
        return f"{minutes} minute{'s' if minutes > 1 else ''}"
    else:
        hours = int(total_seconds / 3600)
        minutes = int((total_seconds % 3600) / 60)
        return f"{hours} hour{'s' if hours > 1 else ''} {minutes} minute{'s' if minutes > 1 else ''}"

def validate_url(url: str) -> bool:
    """
    Validate URL format
    
    Args:
        url: URL string
        
    Returns:
        True if valid URL
    """
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url_pattern.match(url) is not None

def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely divide two numbers
    
    Args:
        numerator: Numerator
        denominator: Denominator
        default: Default value if division by zero
        
    Returns:
        Division result or default
    """
    try:
        if denominator == 0:
            return default
        return numerator / denominator
    except:
        return default

def bytes_to_human_readable(bytes_size: int) -> str:
    """
    Convert bytes to human readable format
    
    Args:
        bytes_size: Size in bytes
        
    Returns:
        Human readable size string
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} PB"