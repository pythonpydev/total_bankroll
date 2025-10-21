import os
from dotenv import load_dotenv

# Determine the base directory of the project
basedir = os.path.abspath(os.path.dirname(__file__))
# Construct the path to the .env file
dotenv_path = os.path.join(basedir, '..', '..', '.env')
load_dotenv(dotenv_path=dotenv_path)

# Debug: Confirm .env file exists
if not os.path.exists(dotenv_path):
    print(f"Error: .env file not found at {dotenv_path}")
else:
    print(f"Loaded .env file from {dotenv_path}")

class Config:
    """Base configuration settings."""
    # General Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'a-default-dev-secret-key')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask-Security-Too settings
    SECURITY_PASSWORD_SALT = os.getenv('SECURITY_PASSWORD_SALT')
    SECURITY_PASSWORD_HASH = 'argon2'
    SECURITY_REGISTERABLE = True
    SECURITY_SEND_REGISTER_EMAIL = True
    SECURITY_CONFIRMABLE = True
    SECURITY_RECOVERABLE = True
    SECURITY_CHANGEABLE = True
    SECURITY_UNAUTHORIZED_VIEW = '/'
    SECURITY_OAUTH_ENABLE = False

    # Flask-Mail settings
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'true').lower() in ['true', '1', 't']
    MAIL_USE_SSL = os.getenv('MAIL_USE_SSL', 'false').lower() in ['true', '1', 't']
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', MAIL_USERNAME)

    # Google OAuth
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{os.getenv('DEV_DB_USER')}:{os.getenv('DEV_DB_PASS')}@"
        f"{os.getenv('DEV_DB_HOST')}/{os.getenv('DEV_DB_NAME')}"
    )

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') or (
        f"mysql+pymysql://{os.getenv('DB_USER_PROD')}:{os.getenv('DB_PASS_PROD')}@"
        f"{os.getenv('DB_HOST_PROD')}/{os.getenv('DB_NAME_PROD')}"
    )
    # Debug: Print database configuration
    print(f"ProductionConfig - DATABASE_URL: {os.getenv('DATABASE_URL')}")
    print(f"ProductionConfig - DB_USER_PROD: {os.getenv('DB_USER_PROD')}")
    print(f"ProductionConfig - DB_PASS_PROD: {os.getenv('DB_PASS_PROD')}")
    print(f"ProductionConfig - DB_HOST_PROD: {os.getenv('DB_HOST_PROD')}")
    print(f"ProductionConfig - DB_NAME_PROD: {os.getenv('DB_NAME_PROD')}")
    print(f"ProductionConfig - SQLALCHEMY_DATABASE_URI: {SQLALCHEMY_DATABASE_URI}")

config_by_name = dict(
    development=DevelopmentConfig,
    production=ProductionConfig
)
