import os
__version__ = "0.1.0"
from flask import Flask, session, flash
from dotenv import load_dotenv
from flask_security import Security, SQLAlchemyUserDatastore
from flask_login import LoginManager
from flask_dance.contrib.google import make_google_blueprint
from flask_dance.contrib.facebook import make_facebook_blueprint
from flask_dance.consumer.storage.sqla import SQLAlchemyStorage
from flask_dance.consumer import oauth_authorized
from .config import config 
import logging
from flask_security import current_user
from datetime import datetime
from .extensions import db, mail, csrf
from . import commands
from flask_migrate import Migrate

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def create_app():
    # Load environment variables from .env file
    load_dotenv()

    # Get the absolute path to the directory containing app.py
    basedir = os.path.abspath(os.path.dirname(__file__))

    # App initialization
    app = Flask(__name__, template_folder=os.path.join(basedir, 'templates'))
    app.config.from_object(config[os.getenv('FLASK_ENV', 'development')])
    
    # Initialize CSRFProtect
    csrf.init_app(app)

    db.init_app(app)
    mail.init_app(app)
    migrate = Migrate(app, db)

    from .models import User, OAuth
    from .currency import init_currency_command
    app.cli.add_command(init_currency_command)
    commands.register_commands(app)

    @app.after_request
    def add_security_headers(response):
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        return response

    # Initialize Flask-Security
    user_datastore = SQLAlchemyUserDatastore(db, User, None)
    security = Security(app, user_datastore)

    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        if user_id is None or user_id == 'None':
            return None
        try:
            return user_datastore.find_user(id=int(user_id))
        except Exception as e:
            logger.error(f"Error loading user: {e}")
            return None

    # Clear invalid sessions
    @app.before_request
    def clear_invalid_session():
        if not current_user.is_authenticated and '_user_id' in session and (session['_user_id'] is None or session['_user_id'] == 'None'):
            session.pop('_user_id', None)

    # OAuth Blueprints
    google_bp = make_google_blueprint(
        client_id=os.getenv('GOOGLE_CLIENT_ID'),
        client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
        redirect_to='home.home',
        scope=['openid', 'email', 'profile']
    )
    app.register_blueprint(google_bp, url_prefix='/security/google')
    

    # Conditionally register Facebook blueprint
    facebook_enabled = os.getenv('FACEBOOK_CLIENT_ID') and os.getenv('FACEBOOK_CLIENT_SECRET')
    if facebook_enabled:
        facebook_bp = make_facebook_blueprint(
            client_id=os.getenv('FACEBOOK_CLIENT_ID'),
            client_secret=os.getenv('FACEBOOK_CLIENT_SECRET'),
            redirect_to='home.home',
            scope=['email']
        )
        app.register_blueprint(facebook_bp, url_prefix='/security/facebook')
    else:
        logger.warning("Facebook OAuth credentials not provided. Facebook login disabled.")

    # OAuth Storage
    google_bp.storage = SQLAlchemyStorage(OAuth, db.session, user=current_user)
    if facebook_enabled:
        facebook_bp.storage = SQLAlchemyStorage(OAuth, db.session, user=current_user)

    from flask_security import login_user

    def _get_or_create_oauth_user(provider_name, user_info, token, user_datastore):
        """
        Finds an existing user or creates a new one for OAuth login.
        Also creates or updates the OAuth link.
        """
        email = user_info.get("email")
        if not email:
            flash(f"Email not provided by {provider_name.title()}.", 'danger')
            return False

        # Find or create user
        user = user_datastore.find_user(email=email)
        if not user:
            user = user_datastore.create_user(
                email=email,
                fs_uniquifier=os.urandom(24).hex(),
                active=True,
                is_confirmed=True,
                confirmed_on=datetime.utcnow(),
                created_at=datetime.utcnow()
            )
        
        # Find or create OAuth link
        provider_user_id = user_info['id']
        oauth = OAuth.query.filter_by(provider=provider_name, provider_user_id=provider_user_id).first()
        if not oauth:
            oauth = OAuth(provider=provider_name, provider_user_id=provider_user_id, token=token, user=user)
            db.session.add(oauth)
        else:
            oauth.token = token # Update token

        user.last_login_at = datetime.utcnow()
        db.session.commit()
        login_user(user)
        flash(f'Logged in successfully with {provider_name.title()}!', 'success')

    # Handle OAuth callbacks
    @oauth_authorized.connect_via(google_bp)
    def google_logged_in(blueprint, token):
        if not token:
            logger.error("Google OAuth token missing")
            flash("Google login failed.", "danger")
            return False

        resp = blueprint.session.get('/oauth2/v2/userinfo')
        if not resp.ok:
            logger.error(f"Failed to fetch user info from Google: {resp.text}")
            flash("Failed to fetch user info from Google.", "danger")
            return False

        user_info = resp.json()
        _get_or_create_oauth_user('google', user_info, token, user_datastore)

    if facebook_enabled:
        @oauth_authorized.connect_via(facebook_bp)
        def facebook_logged_in(blueprint, token):
            if not token:
                logger.error("Facebook OAuth token missing")
                flash("Facebook login failed.", "danger")
                return False

            resp = blueprint.session.get('/me?fields=id,email')
            if not resp.ok:
                logger.error(f"Failed to fetch user info from Facebook: {resp.text}")
                flash("Failed to fetch user info from Facebook.", "danger")
                return False

            user_info = resp.json()
            _get_or_create_oauth_user('facebook', user_info, token, user_datastore)

    # Register blueprints
    from .routes.auth import auth_bp
    from .routes.home import home_bp
    from .routes.poker_sites import poker_sites_bp
    from .routes.assets import assets_bp
    from .routes.withdrawal import withdrawal_bp
    from .routes.deposit import deposit_bp
    from .routes.about import about_bp
    from .routes.charts import charts_bp
    from .routes.settings import settings_bp
    from .routes.reset_db import reset_db_bp
    from .routes.import_db import import_db_bp
    from .routes.common import common_bp
    from .routes.add_withdrawal import add_withdrawal_bp
    from .routes.add_deposit import add_deposit_bp
    from .routes.tools import tools_bp

    app.register_blueprint(auth_bp, url_prefix='/security')
    app.register_blueprint(home_bp)
    app.register_blueprint(poker_sites_bp)
    app.register_blueprint(assets_bp)
    app.register_blueprint(withdrawal_bp)
    app.register_blueprint(deposit_bp)
    app.register_blueprint(about_bp)
    app.register_blueprint(charts_bp, url_prefix='/charts')
    app.register_blueprint(settings_bp)
    app.register_blueprint(reset_db_bp)
    app.register_blueprint(import_db_bp)
    app.register_blueprint(common_bp)
    app.register_blueprint(add_withdrawal_bp)
    app.register_blueprint(add_deposit_bp)
    app.register_blueprint(tools_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
