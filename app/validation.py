"""
Input validation and sanitization utilities
SECURITY FEATURE: Input Validation & Sanitization
"""
import re
from markupsafe import escape
from typing import Tuple


class ValidationError(Exception):
    """Custom validation exception"""
    pass


def sanitize_string(value: str) -> str:
    """
    Sanitize string input to prevent XSS attacks.
    Escapes HTML special characters.
    """
    if not isinstance(value, str):
        raise ValidationError("Input must be a string")
    return escape(value).strip()


def validate_email(email: str) -> bool:
    """
    Validate email format.
    Prevents invalid email addresses from being stored.
    """
    email = sanitize_string(email)
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_username(username: str) -> bool:
    """
    Validate username format.
    Only allows alphanumeric characters, underscores, and hyphens.
    """
    username = sanitize_string(username)
    pattern = r'^[a-zA-Z0-9_-]{3,20}$'
    return bool(re.match(pattern, username))


def validate_password(password: str) -> Tuple[bool, str]:
    """
    Validate password strength.
    Requirements: min 8 chars, uppercase, lowercase, digit, special char.
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain an uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain a lowercase letter"
    if not re.search(r'\d', password):
        return False, "Password must contain a number"
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:,.<>?]', password):
        return False, "Password must contain a special character"
    return True, "Password is valid"


def validate_patient_data(data: dict) -> Tuple[bool, str]:
    """
    Validate patient record data.
    Ensures all required fields are present and valid.
    """
    required_fields = ['gender', 'age', 'hypertension', 'ever_married', 
                      'work_type', 'Residence_type', 'avg_glucose_level', 
                      'bmi', 'smoking_status']
    
    # Check required fields
    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"
    
    # Validate age
    try:
        age = float(data.get('age', 0))
        if age < 0 or age > 120:
            return False, "Age must be between 0 and 120"
    except (ValueError, TypeError):
        return False, "Age must be a valid number"
    
    # Validate glucose level
    try:
        glucose = float(data.get('avg_glucose_level', 0))
        if glucose < 0 or glucose > 500:
            return False, "Glucose level must be between 0 and 500"
    except (ValueError, TypeError):
        return False, "Glucose level must be a valid number"
    
    # Validate BMI
    try:
        bmi = float(data.get('bmi', 0))
        if bmi < 0 or bmi > 100:
            return False, "BMI must be between 0 and 100"
    except (ValueError, TypeError):
        return False, "BMI must be a valid number"
    
    # Validate gender
    valid_genders = ['Male', 'Female', 'Other']
    if sanitize_string(data.get('gender', '')) not in valid_genders:
        return False, f"Gender must be one of {valid_genders}"
    
    # Validate binary fields
    valid_binary = ['0', '1', 0, 1]
    if data.get('hypertension') not in valid_binary:
        return False, "Hypertension must be 0 or 1"
    
    return True, "Data is valid"


def sanitize_patient_data(data: dict) -> dict:
    """
    Sanitize patient data to prevent injection attacks.
    """
    sanitized = {}
    for key, value in data.items():
        if isinstance(value, str):
            sanitized[key] = sanitize_string(value)
        else:
            sanitized[key] = value
    return sanitized
