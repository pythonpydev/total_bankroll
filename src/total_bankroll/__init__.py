from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_security import Security, SQLAlchemyUserDatastore
from .models import db, User, Role, OAuth as OAuthModel
from .extensions import bcrypt, limiter, mail, principal
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
    
    # Initialize Flask-Migrate
    migrate = Migrate(app, db)
    
    # Setup Flask-Security without OAuth
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security = Security(app, user_datastore, register_blueprint=False)
    
    # Initialize OAuth
    from . import oauth
    oauth.init_oauth(app)
    
    # Register blueprints
    from .routes import home_bp
    app.register_blueprint(home_bp)
    
    return app