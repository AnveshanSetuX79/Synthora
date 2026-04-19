"""Password strength validation utilities.

Requirement 14.2: Password complexity - 8+ chars, mixed case, number
"""
import re
from typing import Tuple, List


class PasswordValidationError(Exception):
    """Raised when password doesn't meet complexity requirements."""
    pass


def validate_password_strength(password: str) -> Tuple[bool, List[str]]:
    """Validate password meets complexity requirements.
    
    Requirements (14.2):
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one number
    
    Args:
        password: Password to validate
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    # Check length
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    
    # Check for uppercase
    if not any(c.isupper() for c in password):
        errors.append("Password must contain at least one uppercase letter")
    
    # Check for lowercase
    if not any(c.islower() for c in password):
        errors.append("Password must contain at least one lowercase letter")
    
    # Check for digit
    if not any(c.isdigit() for c in password):
        errors.append("Password must contain at least one number")
    
    # Optional: Check for special characters (recommended but not required)
    # if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
    #     errors.append("Password should contain at least one special character")
    
    # Check for common weak passwords
    weak_passwords = [
        'password', 'password123', '12345678', 'qwerty123',
        'admin123', 'welcome123', 'letmein123'
    ]
    if password.lower() in weak_passwords:
        errors.append("Password is too common. Please choose a stronger password")
    
    is_valid = len(errors) == 0
    return is_valid, errors


def get_password_strength_score(password: str) -> int:
    """Calculate password strength score (0-100).
    
    Args:
        password: Password to evaluate
        
    Returns:
        Score from 0 (very weak) to 100 (very strong)
    """
    score = 0
    
    # Length score (up to 30 points)
    if len(password) >= 8:
        score += 10
    if len(password) >= 12:
        score += 10
    if len(password) >= 16:
        score += 10
    
    # Character variety (up to 40 points)
    if any(c.isupper() for c in password):
        score += 10
    if any(c.islower() for c in password):
        score += 10
    if any(c.isdigit() for c in password):
        score += 10
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        score += 10
    
    # Complexity bonus (up to 30 points)
    # Mix of different character types
    char_types = sum([
        any(c.isupper() for c in password),
        any(c.islower() for c in password),
        any(c.isdigit() for c in password),
        bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
    ])
    score += char_types * 7.5
    
    return min(score, 100)


def get_password_strength_label(score: int) -> str:
    """Get human-readable password strength label.
    
    Args:
        score: Password strength score (0-100)
        
    Returns:
        Strength label
    """
    if score < 40:
        return "Weak"
    elif score < 60:
        return "Fair"
    elif score < 80:
        return "Good"
    else:
        return "Strong"
