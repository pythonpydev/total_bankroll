from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_security import Security, SQLAlchemyUserDatastore, current_user
from .models import db, User, Role, OAuth as OAuthModel
from .extensions import bcrypt, limiter, mail, principal, csrf
from .config import DevelopmentConfig, ProductionConfig
import os
import logging

logger = logging.getLogger(__name__)

def create_app(config_name='development'):
    app = Flask(__name__)
    
    # Load configuration
    available_configs = {
        'development': DevelopmentConfig,
        'production': ProductionConfig
    }
    logger.debug(f"Available configs={list(available_configs.keys())}")
    config = available_configs.get(config_name, DevelopmentConfig)
    logger.debug(f"Selected config={config.__name__}")
    app.config.from_object(config)
    
    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    limiter.init_app(app)
    mail.init_app(app)
    principal.init_app(app)
    csrf.init_app(app)
    
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
        achievements_bp, articles_bp, tools_bp, hand_eval_bp, common_bp
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
    app.register_blueprint(charts_bp)
    app.register_blueprint(goals_bp)
    app.register_blueprint(achievements_bp)
    app.register_blueprint(articles_bp)
    app.register_blueprint(tools_bp)
    app.register_blueprint(hand_eval_bp)
    app.register_blueprint(common_bp)

    # Add a context processor to make current_year available in all templates
    @app.context_processor
    def inject_current_year():
        from datetime import datetime
        return {'current_year': datetime.utcnow().year}
    
    return app