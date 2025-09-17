import os
from dotenv import load_dotenv

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', os.urandom(24).hex())
    EXCHANGE_RATE_API_KEY = os.getenv('EXCHANGE_RATE_API_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {'pool_recycle': 280}
    SESSION_PROTECTION = 'strong'

    # --- Database settings ---
    # Database variables are now defined in environment-specific configs.

    # --- Flask-Security settings ---
    SECURITY_PASSWORD_SALT = os.getenv('SECURITY_PASSWORD_SALT', 'default_salt_please_change')
    SECURITY_PASSWORD_HASH = 'argon2'
    SECURITY_CONFIRMABLE = True
    SECURITY_RECOVERABLE = True
    SECURITY_LOGIN_VIEW = "auth.login"
    SECURITY_LOGOUT_VIEW = "auth.logout"
    SECURITY_REGISTER_VIEW = "auth.register"
    SECURITY_POST_LOGIN_VIEW = "/"
    SECURITY_POST_LOGOUT_VIEW = "auth.login"

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
    
    # --- OAuth settings for templates ---
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')

class DevelopmentConfig(Config):
    DEBUG = True
    SERVER_NAME = '127.0.0.1:5000'
    PREFERRED_URL_SCHEME = 'http'
    # Development-specific database credentials
    DB_USER = os.getenv('DEV_DB_USER')
    DB_PASS = os.getenv('DEV_DB_PASS')
    DB_HOST = os.getenv('DEV_DB_HOST')
    DB_NAME = os.getenv('DEV_DB_NAME')

class ProductionConfig(Config):
    DEBUG = False
    SERVER_NAME = 'www.stakeeasy.net'
    PREFERRED_URL_SCHEME = 'https'
    # Production-specific database credentials using distinct environment variables
    DB_USER = os.getenv('PROD_DB_USER')
    DB_PASS = os.getenv('PROD_DB_PASS')
    DB_HOST = os.getenv('PROD_DB_HOST')
    DB_NAME = os.getenv('PROD_DB_NAME')

class TestingConfig(Config):
    TESTING = True
    # Use an in-memory SQLite database for tests to make them faster
    # and avoid conflicts with the MySQL dev database.
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False  # Disable CSRF for tests
    SECURITY_PASSWORD_SALT = "test-salt"  # Use a static salt for tests
    LOGIN_DISABLED = False  # Make sure login is not disabled
    MAIL_SUPPRESS_SEND = True  # Don't send emails during tests
    SECURITY_LOGIN_VIEW = "auth.login" # Set login view for tests before security is initialized
    SERVER_NAME = "localhost.localdomain" # Required for url_for to work in tests

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
