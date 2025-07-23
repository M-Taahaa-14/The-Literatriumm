import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() in ['true', '1', 'yes']
    
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:3000').split(',')
    
    ANALYTICS_CACHE_TIMEOUT = int(os.environ.get('ANALYTICS_CACHE_TIMEOUT', 300))
    MAX_RECORDS_PER_QUERY = int(os.environ.get('MAX_RECORDS_PER_QUERY', 1000))
    
    DJANGO_API_BASE_URL = os.environ.get('DJANGO_API_BASE_URL', 'http://localhost:8000/api')
    DJANGO_API_TOKEN = os.environ.get('DJANGO_API_TOKEN', '')


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}