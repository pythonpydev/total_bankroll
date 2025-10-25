import os
__version__ = "0.1.0"
from flask import Flask, session, flash, redirect, url_for, current_app, g, request
from flask_security import Security, SQLAlchemyUserDatastore
from .config import config_by_name
from jinja2 import pass_context
from markupsafe import Markup
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from .extensions import db, mail, csrf
from . import commands
from flask_migrate import Migrate
import requests
from bs4 import BeautifulSoup
import bleach

# --- Blueprint Imports ---
from .routes.auth import auth_bp
from .routes.home import home_bp
from .routes.poker_sites import poker_sites_bp
from .routes.articles import articles_bp
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
from .routes.goals import goals_bp
from .routes.help import help_bp
from .routes.hand_eval import load_plo_hand_rankings_data

logger = logging.getLogger(__name__)

def register_blueprints(app):
    """Registers all blueprints for the application."""
    blueprints = [
        (auth_bp, '/auth'), (home_bp, None), (poker_sites_bp, None),
        (assets_bp, None), (withdrawal_bp, None), (deposit_bp, None),
        (about_bp, None), (charts_bp, '/charts'), (settings_bp, None),
        (reset_db_bp, None), (import_db_bp, None), (common_bp, None),
        (add_withdrawal_bp, None), (add_deposit_bp, None), (tools_bp, None),
        (hand_eval_bp, '/hand-eval'), (legal_bp, None), (goals_bp, None), (help_bp, None),
        (articles_bp, None),
    ]
    for bp, url_prefix in blueprints:
        app.register_blueprint(bp, url_prefix=url_prefix)

    with app.app_context():
        load_plo_hand_rankings_data(app)

def create_app(config_name=None):
    basedir = os.path.abspath(os.path.dirname(__file__))
    app = Flask(__name__, template_folder=os.path.join(basedir, 'templates'))
    config_name = config_name or os.getenv('FLASK_ENV', 'production')
    config_obj = config_by_name[config_name]
    print(f"create_app: Using config_name={config_name}")
    print(f"create_app: Available configs={list(config_by_name.keys())}")
    app.config.from_object(config_obj)
    print(f"create_app: Selected config={config_obj.__class__.__name__}")
    print(f"create_app: SQLALCHEMY_DATABASE_URI={app.config['SQLALCHEMY_DATABASE_URI']}")
    app.config['CONFIG_SOURCE'] = config_obj.__class__.__name__
    app.config['GOOGLE_CLIENT_ID'] = os.getenv('GOOGLE_CLIENT_ID')

    log_level = logging.DEBUG if app.config.get('DEBUG', False) else logging.INFO
    logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

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

    user_datastore = SQLAlchemyUserDatastore(db, User, None)
    security = Security(app, user_datastore, register_blueprint=False)

    @app.login_manager.unauthorized_handler
    def unauthn_handler():
        return redirect(url_for("auth.login"))

    from . import oauth
    oauth.init_oauth(app)

    @pass_context
    def truncate_html(context, html, length):
        if not html:
            return ""
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text()
        if len(text) <= length:
            return str(soup)
        current_length = 0
        truncated_soup = BeautifulSoup('<div></div>', 'html.parser')
        div = truncated_soup.div
        for element in soup.children:
            if element.name:
                element_text = element.get_text()
                if current_length + len(element_text) > length:
                    remaining = length - current_length
                    if remaining > 0:
                        truncated_text = element_text[:remaining] + "..."
                        new_element = truncated_soup.new_tag(element.name)
                        new_element.string = truncated_text
                        div.append(new_element)
                    break
                else:
                    div.append(element)
                    current_length += len(element_text)
            else:
                if current_length < length:
                    remaining = length - current_length
                    truncated_text = element[:remaining] + ("..." if len(element) > remaining else "")
                    div.append(truncated_text)
                    current_length += len(element)
                    if current_length >= length:
                        break
        allowed_tags = ['div', 'p', 'h1', 'h2', 'h3', 'h4', 'strong', 'em', 'span', 'table', 'tr', 'th', 'td', 'thead', 'tbody', 'ul', 'ol', 'li']
        allowed_attributes = {'span': ['class'], 'table': ['class'], 'th': ['class'], 'td': ['class']}
        return bleach.clean(str(div), tags=allowed_tags, attributes=allowed_attributes)

    app.jinja_env.filters['truncate_html'] = truncate_html
    register_blueprints(app)

    @app.before_request
    def before_request_handler():
        if 'is_in_eu' not in session:
            g.is_in_eu = False
            try:
                ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
                if ip_address == '127.0.0.1':
                    ip_address = '8.8.8.8'
                response = requests.get(f'http://ip-api.com/json/{ip_address}?fields=countryCode', timeout=5)
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
                session['is_in_eu'] = False
        g.is_in_eu = session.get('is_in_eu', False)
        cookie_consent = request.cookies.get('cookie_consent')
        g.cookie_consent_given = cookie_consent == 'true'

    @app.context_processor
    def inject_config_variables():
        return dict(config=current_app.config)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
