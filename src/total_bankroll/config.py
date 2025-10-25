import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))  # /home/ed/MEGA/total_bankroll/src/total_bankroll
env_paths = [
    os.path.join(basedir, '../../.env'),  # /home/ed/MEGA/total_bankroll/.env
    os.path.join(basedir, '../.env')      # /home/ed/MEGA/total_bankroll/src/.env
]
env_loaded = False
for env_path in env_paths:
    print(f"Attempting to load .env from: {env_path}")
    if os.path.exists(env_path):
        print(f".env file exists at {env_path}")
        with open(env_path, 'r') as f:
            print(f".env contents:\n{f.read()}")
        load_dotenv(dotenv_path=env_path, override=True)
        env_loaded = True
        break
if not env_loaded:
    print(f"No .env file found at {env_paths}")
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
    development=DevelopmentConfig(),
    production=ProductionConfig()
)