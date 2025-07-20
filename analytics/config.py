"""
Configuration settings for Flask Analytics Microservice
"""

import os
from datetime import timedelta


class Config:
    """Base configuration class."""
    
    # Flask Settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'analytics-dev-secret-key-change-in-production'
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() in ['true', '1', 'yes']
    
    # Database Configuration - PostgreSQL
    DATABASE_URL = os.environ.get('DATABASE_URL') or \
        'postgresql://postgres:password@localhost:5432/library_analytics'
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # CORS Settings
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:3000').split(',')
    
    # Analytics Settings
    ANALYTICS_CACHE_TIMEOUT = int(os.environ.get('ANALYTICS_CACHE_TIMEOUT', 300))  # 5 minutes
    MAX_RECORDS_PER_QUERY = int(os.environ.get('MAX_RECORDS_PER_QUERY', 1000))
    
    # Django API Settings (for data sync)
    DJANGO_API_BASE_URL = os.environ.get('DJANGO_API_BASE_URL', 'http://localhost:8000/api')
    DJANGO_API_TOKEN = os.environ.get('DJANGO_API_TOKEN', '')


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'postgresql://postgres:password@localhost:5432/library_analytics_dev'


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY')  # Must be set in production
    
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable must be set in production")


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # In-memory SQLite for tests
    WTF_CSRF_ENABLED = False


# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
