import os
from datetime import timedelta

# Application Configuration
DEBUG = True
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Database Configuration - SQLite for User Authentication
SQLALCHEMY_DATABASE_URI = 'sqlite:///hospital_auth.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# MongoDB Configuration for Patient Records
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/stroke_prediction')

# Session Configuration
PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# Security Settings
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
WTF_CSRF_TIME_LIMIT = None
WTF_CSRF_ENABLED = True
