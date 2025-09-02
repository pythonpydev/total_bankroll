import os
import json
from flask import flash, redirect, url_for, current_app
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.contrib.facebook import make_facebook_blueprint, facebook
from flask_dance.consumer.storage.sqla import SQLAlchemyStorage
from flask_dance.consumer import oauth_authorized
from flask_security import login_user, current_user
from .models import User, OAuth
from .extensions import db
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def _login_or_create_oauth_user(provider_name, user_info, user_datastore):
    """
    Finds an existing user or creates a new one for OAuth login.
    Returns the user object on success, or None on failure.
    """
    try:
        logger.info(f"Starting _login_or_create_oauth_user for provider: {provider_name}")

        email = user_info.get("email")
        if not email:
            flash(f"Email not provided by {provider_name.title()}.", 'danger')
            logger.error(f"Email missing in OAuth callback from {provider_name}. Info: {user_info}")
            return None
        
        logger.info(f"Looking for user with email: {email}")
        user = user_datastore.find_user(email=email)
        
        if not user:
            logger.info(f"User not found. Creating new user for {email}.")
            user = User(
                email=email,
                fs_uniquifier=os.urandom(24).hex(),
                active=True,
                is_confirmed=True,
                confirmed_on=datetime.utcnow(),
                created_at=datetime.utcnow()
            )
            db.session.add(user)
            logger.info("New user object added to session.")
        else:
            logger.info(f"Found existing user with ID: {user.id}")

        user.last_login_at = datetime.utcnow()
        logger.info("Committing user transaction to database.")
        db.session.commit()
        logger.info("Transaction committed.")
        
        return user
    except Exception as e:
        logger.critical(f"UNCAUGHT EXCEPTION IN _login_or_create_oauth_user: {e}", exc_info=True)
        db.session.rollback()
        flash("A database error occurred during login.", "danger")
        return None

def init_oauth(app):
    # OAuth Blueprints
    google_client_id = os.getenv('GOOGLE_CLIENT_ID')
    google_client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
    if google_client_id and google_client_secret:
        google_bp = make_google_blueprint(
            client_id=google_client_id,
            client_secret=google_client_secret,
            scope=[
                "openid",
                "https://www.googleapis.com/auth/userinfo.email",
                "https://www.googleapis.com/auth/userinfo.profile",
            ],
            storage=SQLAlchemyStorage(OAuth, db.session, user=current_user)
        )
        app.register_blueprint(google_bp, url_prefix='/login')

        @oauth_authorized.connect_via(google_bp)
        def google_logged_in(blueprint, token):
            try:
                if not token:
                    flash("Google login failed.", "danger")
                    return redirect(url_for("auth.login"))
                resp = google.get('/oauth2/v2/userinfo')
                if not resp.ok:
                    flash("Failed to fetch user info from Google.", "danger")
                    return redirect(url_for("auth.login"))
                user_info = resp.json()
                user_datastore = current_app.extensions['security'].datastore
                user = _login_or_create_oauth_user('google', user_info, user_datastore)
                if user:
                    login_user(user, remember=True)
                    flash(f'Logged in successfully with Google!', 'success')
                    return redirect(url_for("home.home"))
                return redirect(url_for("auth.login"))
            except Exception as e:
                logger.critical(f"UNCAUGHT EXCEPTION IN google_logged_in: {e}", exc_info=True)
                flash("An unexpected error occurred during login. Please try again.", "danger")
                return redirect(url_for("auth.login"))
    else:
        logger.warning("Google OAuth credentials not provided. Google login disabled.")

    # Conditionally register Facebook blueprint
    facebook_enabled = os.getenv('FACEBOOK_CLIENT_ID') and os.getenv('FACEBOOK_CLIENT_SECRET')
    if facebook_enabled:
        facebook_bp = make_facebook_blueprint(
            client_id=os.getenv('FACEBOOK_CLIENT_ID'),
            client_secret=os.getenv('FACEBOOK_CLIENT_SECRET'),
            scope=['email'],
            storage=SQLAlchemyStorage(OAuth, db.session, user=current_user)
        )
        app.register_blueprint(facebook_bp, url_prefix='/login')

        @oauth_authorized.connect_via(facebook_bp)
        def facebook_logged_in(blueprint, token):
            # This is a placeholder. Implement full logic similar to google_logged_in if needed.
            flash("Facebook login is not fully implemented yet.", "info")
            return redirect(url_for("auth.login"))
    else:
        logger.warning("Facebook OAuth credentials not provided. Facebook login disabled.")