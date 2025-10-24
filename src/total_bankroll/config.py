import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
dotenv_path = os.getenv('DOTENV_PATH', os.path.join(basedir, '../.env'))
load_dotenv(dotenv_path=dotenv_path, override=True)

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
    SECURITY_OAUTH_ENABLE = True
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'true').lower() in ['true', '1', 't']
    MAIL_USE_SSL = os.getenv('MAIL_USE_SSL', 'false').lower() in ['true', '1', 't']
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', MAIL_USERNAME)
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')

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