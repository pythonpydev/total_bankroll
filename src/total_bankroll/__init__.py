import os
__version__ = "0.1.0"
from flask import Flask, session, flash, redirect, url_for, current_app
from dotenv import load_dotenv
from flask_security import Security, SQLAlchemyUserDatastore, current_user
from flask_dance.contrib.google import make_google_blueprint
from flask_dance.contrib.facebook import make_facebook_blueprint
from flask_dance.consumer.storage.sqla import SQLAlchemyStorage
from flask_dance.consumer import oauth_authorized 
from .config import config 
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from .extensions import db, mail, csrf
from . import commands
from flask_migrate import Migrate

logger = logging.getLogger(__name__)

def register_blueprints(app):
    """Registers all blueprints for the application."""
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

    blueprints = [
        (auth_bp, '/security'), (home_bp, None), (poker_sites_bp, None),
        (assets_bp, None), (withdrawal_bp, None), (deposit_bp, None),
        (about_bp, None), (charts_bp, '/charts'), (settings_bp, None),
        (reset_db_bp, None), (import_db_bp, None), (common_bp, None),
        (add_withdrawal_bp, None), (add_deposit_bp, None), (tools_bp, None)
    ]
    for bp, url_prefix in blueprints:
        app.register_blueprint(bp, url_prefix=url_prefix)

def create_app():
    # Load environment variables from .env file
    load_dotenv()

    # Get the absolute path to the directory containing app.py
    basedir = os.path.abspath(os.path.dirname(__file__))

    # App initialization
    app = Flask(__name__, template_folder=os.path.join(basedir, 'templates'))
    app.config.from_object(config[os.getenv('FLASK_ENV', 'development')])
    
    # Configure logging to stream to console (stderr), which PythonAnywhere captures
    log_level = logging.DEBUG if app.config['DEBUG'] else logging.INFO
    logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
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

    # OAuth Blueprints
    google_client_id = os.getenv('GOOGLE_CLIENT_ID')
    google_client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
    if google_client_id and google_client_secret:
        google_bp = make_google_blueprint(
            client_id=google_client_id,
            client_secret=google_client_secret,
            scope=['openid', 'email', 'profile']
        )
        app.register_blueprint(google_bp, url_prefix='/login')
    else:
        logger.warning("Google OAuth credentials not provided. Google login disabled.")

    # Conditionally register Facebook blueprint
    facebook_enabled = os.getenv('FACEBOOK_CLIENT_ID') and os.getenv('FACEBOOK_CLIENT_SECRET')
    if facebook_enabled:
        facebook_bp = make_facebook_blueprint(
            client_id=os.getenv('FACEBOOK_CLIENT_ID'),
            client_secret=os.getenv('FACEBOOK_CLIENT_SECRET'),
            # redirect_to='home.home', # We will handle the redirect manually
            scope=['email']
        )
        app.register_blueprint(facebook_bp, url_prefix='/login')
    else:
        logger.warning("Facebook OAuth credentials not provided. Facebook login disabled.")

    import json
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
            # Create user manually to bypass datastore role issues
            user = User(
                email=email,
                fs_uniquifier=os.urandom(24).hex(),
                active=True,
                is_confirmed=True,
                confirmed_on=datetime.utcnow(),
                created_at=datetime.utcnow()
            )
            db.session.add(user)
            # Flush to get the user ID for the OAuth object relationship
            db.session.flush()

        # Find or create OAuth link
        provider_user_id = user_info['id']
        oauth = OAuth.query.filter_by(provider=provider_name, provider_user_id=provider_user_id).first()
        
        # Serialize token to JSON string for storage
        token_json = json.dumps(token)

        if not oauth:
            oauth = OAuth(provider=provider_name, provider_user_id=provider_user_id, token=token_json, user=user)
            db.session.add(oauth)
        else:
            oauth.token = token_json # Update token

        user.last_login_at = datetime.utcnow()
        db.session.commit()
        login_user(user, remember=True)
        flash(f'Logged in successfully with {provider_name.title()}!', 'success')

    # Handle OAuth callbacks
    if google_client_id and google_client_secret:
        @oauth_authorized.connect_via(google_bp)
        def google_logged_in(blueprint, token):
            if not token:
                flash("Google login failed.", "danger")
                return redirect(url_for("auth.login"))

            resp = blueprint.session.get('/oauth2/v2/userinfo')
            if not resp.ok:
                logger.error(f"Failed to fetch user info from Google: {resp.text}")
                flash("Failed to fetch user info from Google.", "danger")
                return redirect(url_for("auth.login"))

            user_info = resp.json()
            user_datastore = current_app.extensions['security'].datastore
            _get_or_create_oauth_user('google', user_info, token, user_datastore)
            return redirect(url_for("home.home"))

    if facebook_enabled:
        @oauth_authorized.connect_via(facebook_bp)
        def facebook_logged_in(blueprint, token):
            if not token:
                logger.error("Facebook OAuth token missing")
                flash("Facebook login failed.", "danger")
                return redirect(url_for("auth.login"))

            resp = blueprint.session.get('/me?fields=id,email')
            if not resp.ok:
                logger.error(f"Failed to fetch user info from Facebook: {resp.text}")
                flash("Failed to fetch user info from Facebook.", "danger")
                return redirect(url_for("auth.login"))

            user_info = resp.json()
            user_datastore = current_app.extensions['security'].datastore
            _get_or_create_oauth_user('facebook', user_info, token, user_datastore)
            return redirect(url_for("home.home"))

    register_blueprints(app)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
