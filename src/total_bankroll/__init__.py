from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_security import Security, SQLAlchemyUserDatastore, current_user
from flask_talisman import Talisman
from .models import db, User, Role, OAuth as OAuthModel
from .vite_asset_helper import init_vite_asset_helper
from .extensions import bcrypt, cache, limiter, mail, principal, csrf
from .config import DevelopmentConfig, ProductionConfig
import os
import logging

logger = logging.getLogger(__name__)

def create_app(config_name=None):
    app = Flask(__name__)
    
    # Determine config_name based on FLASK_ENV
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development').lower()
    logger.debug(f"FLASK_ENV={config_name}")
    
    # Load configuration
    available_configs = {
        'development': DevelopmentConfig,
        'production': ProductionConfig
    }
    config = available_configs.get(config_name, DevelopmentConfig)
    logger.debug(f"Selected config={config.__name__}")
    app.config.from_object(config)
    logger.debug(f"SQLALCHEMY_DATABASE_URI={app.config.get('SQLALCHEMY_DATABASE_URI')}")
    
    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    cache.init_app(app)
    limiter.init_app(app)
    mail.init_app(app)
    principal.init_app(app)
    csrf.init_app(app)
    
    # Initialize Flask-Talisman for security headers (production only)
    if config_name == 'production':
        # Content Security Policy configuration
        csp = {
            'default-src': [
                "'self'",
            ],
            'script-src': [
                "'self'",
                "'unsafe-inline'",  # Needed for inline scripts (Google Analytics, etc.)
                'https://www.googletagmanager.com',
                'https://cdn.jsdelivr.net',
                'https://cdnjs.cloudflare.com',
            ],
            'style-src': [
                "'self'",
                "'unsafe-inline'",  # Needed for inline styles
                'https://cdn.jsdelivr.net',
                'https://cdnjs.cloudflare.com',
                'https://fonts.googleapis.com',
            ],
            'font-src': [
                "'self'",
                'https://cdn.jsdelivr.net',
                'https://cdnjs.cloudflare.com',
                'https://fonts.gstatic.com',
            ],
            'img-src': [
                "'self'",
                'data:',  # For inline images
                'https:',  # Allow images from any HTTPS source
            ],
            'connect-src': [
                "'self'",
            ],
        }
        
        Talisman(
            app,
            content_security_policy=csp,
            content_security_policy_nonce_in=['script-src'],
            force_https=True,  # Redirect HTTP to HTTPS
            strict_transport_security=True,  # HSTS header
            strict_transport_security_max_age=31536000,  # 1 year
        )
    
    # Initialize Flask-Migrate
    migrate = Migrate(app, db)
    
    # Setup Flask-Security without OAuth
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security = Security(app, user_datastore, register_blueprint=False)
    
    # Initialize OAuth
    from . import oauth
    oauth.init_oauth(app)
    
    # Register blueprints
    from .routes import (
        home_bp, about_bp, help_bp, legal_bp, auth_bp, settings_bp,
        poker_sites_bp, assets_bp, deposit_bp, withdrawal_bp,
        add_deposit_bp, add_withdrawal_bp, charts_bp, goals_bp,
        achievements_bp, articles_bp, tools_bp, hand_eval_bp, common_bp,
        import_db_bp
    )
    app.register_blueprint(home_bp)
    app.register_blueprint(about_bp)
    app.register_blueprint(help_bp)
    app.register_blueprint(legal_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(poker_sites_bp)
    app.register_blueprint(assets_bp)
    app.register_blueprint(deposit_bp)
    app.register_blueprint(withdrawal_bp)
    app.register_blueprint(add_deposit_bp)
    app.register_blueprint(add_withdrawal_bp)
    app.register_blueprint(charts_bp, url_prefix='/charts')
    app.register_blueprint(goals_bp)
    app.register_blueprint(achievements_bp)
    app.register_blueprint(articles_bp)
    app.register_blueprint(tools_bp)
    app.register_blueprint(hand_eval_bp)
    app.register_blueprint(common_bp)
    app.register_blueprint(import_db_bp)

    # Initialize Vite asset helper
    init_vite_asset_helper(app)

    from .routes.hand_eval import load_plo_hand_rankings_data
    with app.app_context():
        load_plo_hand_rankings_data(app)

    # Add a context processor to make current_year available in all templates
    @app.context_processor
    def inject_current_year():
        from datetime import datetime
        return {'current_year': datetime.utcnow().year}
    
    return app