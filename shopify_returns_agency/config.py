import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration class"""
    
    def __init__(self):
        # Load configuration from environment variables at initialization
        self.SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
        self.SHOPIFY_WEBHOOK_SECRET = os.environ.get('SHOPIFY_WEBHOOK_SECRET')
        self.WEBHOOK_ENDPOINT = '/shopify/returns-webhook'
        self.LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
        self.LOG_FILE_PATH = os.path.join(os.path.dirname(__file__), 'logs', 'returns_agent.log')
        self.RETURN_WINDOW_DAYS = int(os.environ.get('RETURN_WINDOW_DAYS') or '30')
        self.FLASK_PORT = int(os.environ.get('FLASK_PORT') or '5000')
        self.FLASK_HOST = os.environ.get('FLASK_HOST') or '0.0.0.0'
    
class DevelopmentConfig(Config):
    """Development configuration"""
    def __init__(self):
        super().__init__()
        self.DEBUG = True
        self.TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    def __init__(self):
        super().__init__()
        self.DEBUG = False
        self.TESTING = False

class TestingConfig(Config):
    """Testing configuration"""
    def __init__(self):
        super().__init__()
        self.DEBUG = True
        self.TESTING = True
        self.LOG_LEVEL = 'DEBUG'

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
} 