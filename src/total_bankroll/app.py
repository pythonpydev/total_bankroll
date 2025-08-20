import os
from flask import Flask, session
from dotenv import load_dotenv
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_dance.contrib.google import make_google_blueprint
from flask_dance.contrib.facebook import make_facebook_blueprint
from flask_dance.consumer.storage.sqla import SQLAlchemyStorage
from flask_dance.consumer import oauth_authorized
from flask_mail import Mail
from total_bankroll.config import config
import logging
from flask_security import current_user
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
logger.debug(f"Environment variables before load_dotenv: {os.environ.get('SECURITY_PASSWORD_SALT')}")
load_dotenv()
logger.debug(f"Environment variables after load_dotenv: {os.environ.get('SECURITY_PASSWORD_SALT')}")

# Get the absolute path to the directory containing app.py
basedir = os.path.abspath(os.path.dirname(__file__))

# App initialization
app = Flask(__name__, template_folder=os.path.join(basedir, 'templates'))
app.config.from_object(config[os.getenv('FLASK_ENV', 'development')])

# Construct the database URI for MySQL
db_user = os.getenv('DB_USER', 'root')
db_pass = os.getenv('DB_PASS', 'f3gWoQe7X7BFCm')
db_host = os.getenv('DB_HOST', 'localhost')
db_name = os.getenv('DB_NAME', 'bankroll')
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_pass}@{db_host}/{db_name}'
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SECURITY_PASSWORD_SALT'] = os.getenv('SECURITY_PASSWORD_SALT', 'default_salt_if_missing')
app.config['SECURITY_PASSWORD_HASH'] = 'argon2'
app.config['SECURITY_PASSWORD_SINGLE_HASH'] = False  # Added for compatibility
app.config['SESSION_PROTECTION'] = 'strong'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Mail configuration
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'true').lower() == 'true'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME')

# Flask-Security configuration
app.config['SECURITY_CONFIRMABLE'] = True
app.config['SECURITY_RECOVERABLE'] = True

# Log configuration values
logger.debug(f"SECRET_KEY: {'set' if app.config['SECRET_KEY'] else 'not set'}")
logger.debug(f"SECURITY_PASSWORD_SALT: {app.config['SECURITY_PASSWORD_SALT']}")
logger.debug(f"SQLALCHEMY_DATABASE_URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
logger.debug(f"MAIL_SERVER: {app.config['MAIL_SERVER']}")

db = SQLAlchemy(app)
mail = Mail(app)

# User model
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=True)  # Nullable for OAuth users
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login_at = db.Column(db.DateTime, nullable=True)
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)
    is_confirmed = db.Column(db.Boolean, default=False, nullable=False)
    confirmed_on = db.Column(db.DateTime, nullable=True)

    def get_id(self):
        return str(self.id)

# OAuth model for social logins
class OAuth(db.Model):
    __tablename__ = 'oauth'
    id = db.Column(db.Integer, primary_key=True)
    provider = db.Column(db.String(50), nullable=False)
    provider_user_id = db.Column(db.String(255), nullable=False)
    token = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', backref=db.backref('oauth', lazy='dynamic'))

# Initialize Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, None)
security = Security(app, user_datastore)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    logger.debug(f"load_user called with user_id: {user_id} (type: {type(user_id)})")
    if user_id is None or user_id == 'None':
        logger.warning("user_id is None or 'None', returning None")
        return None
    try:
        return db.session.get(User, int(user_id))
    except Exception as e:
        logger.error(f"Error loading user: {e}")
        return None

# Clear invalid sessions
@app.before_request
def clear_invalid_session():
    if not current_user.is_authenticated and '_user_id' in session and (session['_user_id'] is None or session['_user_id'] == 'None'):
        logger.debug("Clearing invalid session with user_id: None")
        session.pop('_user_id', None)

# OAuth Blueprints
google_bp = make_google_blueprint(
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    redirect_to='auth.google_auth',
    scope=['openid', 'email', 'profile']
)
app.register_blueprint(google_bp, url_prefix='/security/google')

# Conditionally register Facebook blueprint
facebook_enabled = os.getenv('FACEBOOK_CLIENT_ID') and os.getenv('FACEBOOK_CLIENT_SECRET')
if facebook_enabled:
    facebook_bp = make_facebook_blueprint(
        client_id=os.getenv('FACEBOOK_CLIENT_ID'),
        client_secret=os.getenv('FACEBOOK_CLIENT_SECRET'),
        redirect_to='auth.facebook_auth',
        scope=['email']
    )
    app.register_blueprint(facebook_bp, url_prefix='/security/facebook')
else:
    logger.warning("Facebook OAuth credentials not provided. Facebook login disabled.")

# OAuth Storage
google_bp.storage = SQLAlchemyStorage(OAuth, db.session, user=current_user)
if facebook_enabled:
    facebook_bp.storage = SQLAlchemyStorage(OAuth, db.session, user=current_user)

# Handle OAuth callbacks
@oauth_authorized.connect_via(google_bp)
def google_logged_in(blueprint, token):
    if not token:
        logger.error("Google OAuth token missing")
        return False
    resp = blueprint.session.get('/oauth2/v2/userinfo')
    if resp.ok:
        user_info = resp.json()
        provider_user_id = user_info['id']
        email = user_info['email']
        with db.session.no_autoflush:
            oauth = OAuth.query.filter_by(provider='google', provider_user_id=provider_user_id).first()
            if oauth:
                oauth.user.last_login_at = datetime.utcnow()
                db.session.commit()
                login_user(oauth.user)
                logger.debug(f"Google login: Existing user {oauth.user.email}")
            else:
                user = user_datastore.find_user(email=email)
                if not user:
                    user = user_datastore.create_user(
                        email=email,
                        password_hash=None,
                        fs_uniquifier=os.urandom(24).hex(),
                        active=True,
                        is_confirmed=True,
                        confirmed_on=datetime.utcnow(),
                        created_at=datetime.utcnow(),
                        last_login_at=datetime.utcnow()
                    )
                    db.session.commit()
                    logger.debug(f"Google login: Created user {email}")
                oauth = OAuth(
                    provider='google',
                    provider_user_id=provider_user_id,
                    token=token,
                    user=user
                )
                db.session.add(oauth)
                db.session.commit()
                login_user(user)
                logger.debug(f"Google login: Linked new OAuth for {email}")
    return False

if facebook_enabled:
    @oauth_authorized.connect_via(facebook_bp)
    def facebook_logged_in(blueprint, token):
        if not token:
            logger.error("Facebook OAuth token missing")
            return False
        resp = blueprint.session.get('/me?fields=id,email')
        if resp.ok:
            user_info = resp.json()
            provider_user_id = user_info['id']
            email = user_info['email']
            with db.session.no_autoflush:
                oauth = OAuth.query.filter_by(provider='facebook', provider_user_id=provider_user_id).first()
                if oauth:
                    oauth.user.last_login_at = datetime.utcnow()
                    db.session.commit()
                    login_user(oauth.user)
                    logger.debug(f"Facebook login: Existing user {oauth.user.email}")
                else:
                    user = user_datastore.find_user(email=email)
                    if not user:
                        user = user_datastore.create_user(
                            email=email,
                            password_hash=None,
                            fs_uniquifier=os.urandom(24).hex(),
                            active=True,
                            is_confirmed=True,
                            confirmed_on=datetime.utcnow(),
                            created_at=datetime.utcnow(),
                            last_login_at=datetime.utcnow()
                        )
                        db.session.commit()
                        logger.debug(f"Facebook login: Created user {email}")
                    oauth = OAuth(
                        provider='facebook',
                        provider_user_id=provider_user_id,
                        token=token,
                        user=user
                    )
                    db.session.add(oauth)
                    db.session.commit()
                    login_user(user)
                    logger.debug(f"Facebook login: Linked new OAuth for {email}")
        return False

# Register blueprints
from total_bankroll.routes.auth import auth_bp
from total_bankroll.routes.home import home_bp
from total_bankroll.routes.poker_sites import poker_sites_bp
from total_bankroll.routes.assets import assets_bp
from total_bankroll.routes.withdrawal import withdrawal_bp
from total_bankroll.routes.deposit import deposit_bp
from total_bankroll.routes.currency_update import currency_update_bp
from total_bankroll.routes.about import about_bp
from total_bankroll.routes.charts import charts_bp
from total_bankroll.routes.settings import settings_bp
from total_bankroll.routes.common import common_bp
from total_bankroll.routes.add_withdrawal import add_withdrawal_bp
from total_bankroll.routes.add_deposit import add_deposit_bp

app.register_blueprint(auth_bp, url_prefix='/security')
app.register_blueprint(home_bp)
app.register_blueprint(poker_sites_bp)
app.register_blueprint(assets_bp)
app.register_blueprint(withdrawal_bp)
app.register_blueprint(deposit_bp)
app.register_blueprint(currency_update_bp)
app.register_blueprint(about_bp)
app.register_blueprint(charts_bp)
app.register_blueprint(settings_bp)
app.register_blueprint(common_bp)
app.register_blueprint(add_withdrawal_bp)
app.register_blueprint(add_deposit_bp)

if __name__ == '__main__':
    app.run(debug=True)