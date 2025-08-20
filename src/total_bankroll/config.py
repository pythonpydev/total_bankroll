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

    # --- Mail settings ---
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'true').lower() in ['true', '1', 't']
    MAIL_USE_SSL = os.getenv('MAIL_USE_SSL', 'false').lower() in ['true', '1', 't']
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_USERNAME')

    # --- Flask-Security email integration ---
    SECURITY_EMAIL_SENDER = os.getenv('MAIL_USERNAME')
    SECURITY_EMAIL_SUBJECT_REGISTER = "Please confirm your email"

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