# src/total_bankroll/config.py
import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
dotenv_path = os.getenv('DOTENV_PATH', os.path.join(basedir, '../../.env'))  # Changed to ../../.env for project root

print(f"Attempting to load .env from: {dotenv_path}")
if os.path.exists(dotenv_path):
    print(f".env file exists at {dotenv_path}")
    with open(dotenv_path, 'r') as f:
        print(f".env contents:\n{f.read()}")
else:
    print(f".env file does NOT exist at {dotenv_path}")
load_dotenv(dotenv_path=dotenv_path, override=True)
print(f"FLASK_ENV after load: {os.getenv('FLASK_ENV')}")
print(f"DEV_DB_USER after load: {os.getenv('DEV_DB_USER')}")

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'a-default-dev-secret-key')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECURITY_PASSWORD_SALT = os.getenv('SECURITY_PASSWORD_SALT') or 'a-default-dev-salt'
    SECURITY_PASSWORD_HASH = 'argon2'
    SECURITY_REGISTERABLE = True
    SECURITY_SEND_REGISTER_EMAIL = True
    SECURITY_CONFIRMABLE = True
    SECURITY_RECOVERABLE = True
    SECURITY_CHANGEABLE = True
    SECURITY_UNAUTHORIZED_VIEW = '/'
    SECURITY_BLUEPRINT_NAME = 'auth'  # Must match auth_bp name since register_blueprint=False
    SECURITY_OAUTH_ENABLE = False  # Disable OAuth integration to bypass OAuthGlue
    MAIL_BACKEND = os.getenv('MAIL_BACKEND', 'smtp')
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'true').lower() in ['true', '1', 't']
    MAIL_USE_SSL = os.getenv('MAIL_USE_SSL', 'false').lower() in ['true', '1', 't']
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', MAIL_USERNAME)
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
    
    # Cache Configuration
    CACHE_TYPE = os.getenv('CACHE_TYPE', 'SimpleCache')
    CACHE_DEFAULT_TIMEOUT = int(os.getenv('CACHE_DEFAULT_TIMEOUT', 300))
    
    # Redis Configuration (if using Redis cache)
    CACHE_REDIS_URL = os.getenv('REDIS_URL')
    CACHE_KEY_PREFIX = 'stakeeasy_'

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', (
        f"mysql+pymysql://{os.getenv('DEV_DB_USER')}:{os.getenv('DEV_DB_PASS')}@"
        f"{os.getenv('DEV_DB_HOST')}/{os.getenv('DEV_DB_NAME')}"
    ))

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{os.getenv('DB_USER_PROD')}:{os.getenv('DB_PASS_PROD')}@"
        f"{os.getenv('DB_HOST_PROD')}/{os.getenv('DB_NAME_PROD')}"
    )

config_by_name = dict(
    development=DevelopmentConfig,
    production=ProductionConfig
)