"""
Error handling and logging utilities
SECURITY FEATURE: Error Logging & Monitoring
"""
import logging
import logging.handlers
import os
from datetime import datetime


def setup_logging(app):
    """
    Configure application logging.
    Logs are written to file for security audit trail.
    """
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Configure file handler for security events
    security_handler = logging.handlers.RotatingFileHandler(
        'logs/security.log',
        maxBytes=10485760,  # 10MB
        backupCount=20
    )
    security_handler.setLevel(logging.WARNING)
    security_format = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(name)s: %(message)s [%(filename)s:%(lineno)d]'
    )
    security_handler.setFormatter(security_format)

    # Configure file handler for general application logs
    app_handler = logging.handlers.RotatingFileHandler(
        'logs/app.log',
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    app_handler.setLevel(logging.INFO)
    app_handler.setFormatter(security_format)

    # Configure handler for authentication events
    auth_handler = logging.handlers.RotatingFileHandler(
        'logs/auth.log',
        maxBytes=5242880,  # 5MB
        backupCount=10
    )
    auth_handler.setLevel(logging.INFO)
    auth_handler.setFormatter(security_format)

    # Add handlers to app logger
    app.logger.addHandler(security_handler)
    app.logger.addHandler(app_handler)
    app.logger.addHandler(auth_handler)
    app.logger.setLevel(logging.INFO)

    return app.logger


class SecurityLogger:
    """
    Centralized security event logging.
    """
    @staticmethod
    def log_login_attempt(username: str, success: bool, ip_address: str = None):
        """Log login attempts"""
        event = f"Login {'successful' if success else 'failed'} for user: {username}"
        if ip_address:
            event += f" from IP: {ip_address}"
        logger = logging.getLogger('security')
        level = logging.INFO if success else logging.WARNING
        logger.log(level, event)

    @staticmethod
    def log_patient_access(user_id: str, patient_id: str, action: str):
        """Log patient data access"""
        logger = logging.getLogger('security')
        logger.info(f"User {user_id} performed '{action}' on patient {patient_id}")

    @staticmethod
    def log_validation_error(field: str, error: str, user_id: str = None):
        """Log validation errors"""
        logger = logging.getLogger('security')
        msg = f"Validation error in field '{field}': {error}"
        if user_id:
            msg += f" (User: {user_id})"
        logger.warning(msg)

    @staticmethod
    def log_suspicious_activity(description: str, user_id: str = None):
        """Log suspicious activities"""
        logger = logging.getLogger('security')
        logger.warning(f"Suspicious activity: {description}")
