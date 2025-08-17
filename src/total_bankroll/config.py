import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', os.urandom(24).hex())
    DB_HOST = os.getenv('DB_HOST', 'pythonpydev.mysql.pythonanywhere-services.com')
    DB_NAME = os.getenv('DB_NAME', 'pythonpydev$bankroll')
    DB_USER = os.getenv('DB_USER', 'pythonpydev')
    DB_PASS = os.getenv('DB_PASS', 'f3gWoQe7X7BFCm')
    EXCHANGE_RATE_API_KEY = os.getenv('EXCHANGE_RATE_API_KEY')

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

class TestingConfig(Config):
    TESTING = True
    DEBUG = True

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}