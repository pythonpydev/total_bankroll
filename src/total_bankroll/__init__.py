import os
__version__ = "0.1.0"
from flask import Flask, session, flash, redirect, url_for, current_app, g, request
from dotenv import load_dotenv
from flask_security import Security, SQLAlchemyUserDatastore
from .config import config_by_name
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from .extensions import db, mail, csrf
from . import commands
from flask_migrate import Migrate
import requests

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
    from .routes.hand_eval import hand_eval_bp
    from .routes.legal import legal_bp

    blueprints = [
        (auth_bp, '/auth'), (home_bp, None), (poker_sites_bp, None),
        (assets_bp, None), (withdrawal_bp, None), (deposit_bp, None),
        (about_bp, None), (charts_bp, '/charts'), (settings_bp, None),
        (reset_db_bp, None), (import_db_bp, None), (common_bp, None),
        (add_withdrawal_bp, None), (add_deposit_bp, None), (tools_bp, None), 
        (hand_eval_bp, None), (legal_bp, None),
    ]
    for bp, url_prefix in blueprints:
        app.register_blueprint(bp, url_prefix=url_prefix)

def create_app(config_name=None):
    # Get the absolute path to the directory containing app.py
    basedir = os.path.abspath(os.path.dirname(__file__))

    # App initialization
    app = Flask(__name__, template_folder=os.path.join(basedir, 'templates'))
    config_obj = config_by_name[config_name or os.getenv('FLASK_ENV', 'development')]
    app.config.from_object(config_obj)
    app.config['GOOGLE_CLIENT_ID'] = os.getenv('GOOGLE_CLIENT_ID')

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

    # Initialize Flask-Security and OAuth
    user_datastore = SQLAlchemyUserDatastore(db, User, None)
    # Since we have implemented all auth views in the 'auth' blueprint,
    # we can disable the default blueprint from Flask-Security to avoid
    # route conflicts.
    security = Security(app, user_datastore, register_blueprint=False)

    # Define a custom unauthenticated handler to fix the redirect issue in tests
    @app.login_manager.unauthorized_handler
    def unauthn_handler():
        # Store the URL they were trying to get to.
        return redirect(url_for("auth.login"))

    from . import oauth
    oauth.init_oauth(app)

    register_blueprints(app)
    
    @app.before_request
    def before_request_handler():
        """
        Runs before each request.
        - Checks user's location via IP to determine if they are in the EU for GDPR.
          The result is stored in the session to avoid repeated API calls.
        - Checks the cookie consent cookie to determine if analytics should be loaded.
        """
        # 1. Check user location for EU cookie banner
        if 'is_in_eu' not in session:
            g.is_in_eu = False # Default to false
            try:
                # Use a test IP for local development, otherwise use the request IP
                ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
                if ip_address == '127.0.0.1':
                    ip_address = '8.8.8.8' # Google's DNS for testing non-EU
                    # ip_address = '212.58.244.20' # BBC's IP for testing EU (UK)

                # Use a free geolocation API
                response = requests.get(f'http://ip-api.com/json/{ip_address}?fields=countryCode', timeout=2)
                response.raise_for_status()
                data = response.json()

                eu_countries = {
                    'AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR', 'DE', 'GR',
                    'HU', 'IE', 'IT', 'LV', 'LT', 'LU', 'MT', 'NL', 'PL', 'PT', 'RO', 'SK',
                    'SI', 'ES', 'SE'
                }
                
                if data.get('countryCode') in eu_countries:
                    session['is_in_eu'] = True
                else:
                    session['is_in_eu'] = False

            except (requests.RequestException, ValueError) as e:
                logger.warning(f"Could not determine user location: {e}")
                session['is_in_eu'] = False # Default to not showing banner on error
        g.is_in_eu = session.get('is_in_eu', False)

        # 2. Check for cookie consent to enable/disable analytics
        cookie_consent = request.cookies.get('cookie_consent')
        g.cookie_consent_given = cookie_consent == 'true'

    @app.context_processor
    def inject_config_variables():
        return dict(config=current_app.config)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
