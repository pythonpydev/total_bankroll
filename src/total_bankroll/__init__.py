import os
__version__ = "0.1.0"
from flask import Flask, session, flash, redirect, url_for, current_app
from dotenv import load_dotenv
from flask_security import Security, SQLAlchemyUserDatastore
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
        (auth_bp, '/auth'), (home_bp, None), (poker_sites_bp, None),
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

    # Initialize Flask-Security and OAuth
    user_datastore = SQLAlchemyUserDatastore(db, User, None)
    # Since we have implemented all auth views in the 'auth' blueprint,
    # we can disable the default blueprint from Flask-Security to avoid
    # route conflicts.
    security = Security(app, user_datastore, register_blueprint=False)

    from . import oauth
    oauth.init_oauth(app)

    register_blueprints(app)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
