"""
Authentication Utilities Module
Contains helper functions for password validation, hashing, and other auth-related utilities
"""

import re
from werkzeug.security import generate_password_hash, check_password_hash

def validate_password_strength(password):
    """
    Validate password strength
    Requirements:
    - At least 8 characters long
    - Contains at least one uppercase letter
    - Contains at least one lowercase letter  
    - Contains at least one number
    - Contains at least one special character
    """
    if not password:
        return {'is_valid': False, 'message': 'Password is required'}
    
    if len(password) < 8:
        return {'is_valid': False, 'message': 'Password must be at least 8 characters long'}
    
    if not re.search(r'[A-Z]', password):
        return {'is_valid': False, 'message': 'Password must contain at least one uppercase letter'}
    
    if not re.search(r'[a-z]', password):
        return {'is_valid': False, 'message': 'Password must contain at least one lowercase letter'}
    
    if not re.search(r'\d', password):
        return {'is_valid': False, 'message': 'Password must contain at least one number'}
    
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', password):
        return {'is_valid': False, 'message': 'Password must contain at least one special character'}
    
    return {'is_valid': True, 'message': 'Password is strong'}

def hash_password(password):
    """Hash a password using Werkzeug's security utilities"""
    return generate_password_hash(password)

def check_password(password_hash, password):
    """Check if a password matches its hash"""
    return check_password_hash(password_hash, password)

def validate_email(email):
    """Validate email format"""
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None

def validate_phone(phone):
    """Validate phone number format (basic validation)"""
    if not phone:
        return True  # Phone is optional
    
    # Remove common phone number formatting
    phone_clean = re.sub(r'[\s\-\(\)\+]', '', phone)
    
    # Check if it's all digits and has reasonable length
    return phone_clean.isdigit() and 7 <= len(phone_clean) <= 15
