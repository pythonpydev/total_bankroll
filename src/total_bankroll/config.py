import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', os.urandom(24).hex())
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
    DB_HOST = os.getenv('DEV_DB_HOST', 'localhost')
    DB_NAME = os.getenv('DEV_DB_NAME', 'bankroll')
    DB_USER = os.getenv('DEV_DB_USER', 'root')
    DB_PASS = os.getenv('DEV_DB_PASS', 'f3gWoQe7X7BFCm')
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"

class ProductionConfig(Config):
    DEBUG = False
    DB_HOST = os.getenv('PROD_DB_HOST', 'pythonpydev.mysql.pythonanywhere-services.com')
    DB_NAME = os.getenv('PROD_DB_NAME', 'pythonpydev$bankroll')
    DB_USER = os.getenv('PROD_DB_USER', 'pythonpydev')
    DB_PASS = os.getenv('PROD_DB_PASS', 'f3gWoQe7X7BFCm')
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"

class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    DB_HOST = 'localhost'
    DB_NAME = 'test_bankroll'
    DB_USER = 'root'
    DB_PASS = 'f3gWoQe7X7BFCm'
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
