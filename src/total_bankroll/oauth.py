import os
import json
from flask import flash, redirect, url_for, current_app
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.contrib.twitter import make_twitter_blueprint, twitter
from flask_dance.contrib.facebook import make_facebook_blueprint, facebook
from flask_dance.consumer.storage.sqla import SQLAlchemyStorage
from flask_dance.consumer import oauth_authorized
from flask_security import login_user, current_user
from .models import User, OAuth
from .extensions import db
from datetime import datetime, UTC
import logging

logger = logging.getLogger(__name__)

def init_oauth(app):
    # Google OAuth
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
            storage=SQLAlchemyStorage(OAuth, db.session)
        )
        app.register_blueprint(google_bp, url_prefix='/login/google')
    else:
        logger.warning("Google OAuth credentials not provided. Google login disabled.")

    # Twitter OAuth
    twitter_client_id = os.getenv('TWITTER_CLIENT_ID')
    twitter_client_secret = os.getenv('TWITTER_CLIENT_SECRET')
    if twitter_client_id and twitter_client_secret:
        twitter_bp = make_twitter_blueprint(
            api_key=twitter_client_id,
            api_secret=twitter_client_secret,
            storage=SQLAlchemyStorage(OAuth, db.session)
        )
        app.register_blueprint(twitter_bp, url_prefix='/login/twitter')
    else:
        logger.warning("Twitter OAuth credentials not provided. Twitter login disabled.")

    # Facebook OAuth
    facebook_client_id = os.getenv('FACEBOOK_CLIENT_ID')
    facebook_client_secret = os.getenv('FACEBOOK_CLIENT_SECRET')
    if facebook_client_id and facebook_client_secret:
        facebook_bp = make_facebook_blueprint(
            client_id=facebook_client_id,
            client_secret=facebook_client_secret,
            storage=SQLAlchemyStorage(OAuth, db.session)
        )
        app.register_blueprint(facebook_bp, url_prefix='/login/facebook')
    else:
        logger.warning("Facebook OAuth credentials not provided. Facebook login disabled.")

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
            email = user_info.get("email")
            if not email:
                flash("Email not provided by Google.", 'danger')
                logger.error(f"Email missing in Google OAuth callback. Info: {user_info}")
                return redirect(url_for("auth.login"))

            user_datastore = current_app.extensions['security'].datastore
            
            logger.info(f"Looking for user with email: {email}")
            user = user_datastore.find_user(email=email)

            if not user:
                logger.info(f"User not found. Creating new user for {email}.")
                user = User(
                    email=email,
                    fs_uniquifier=os.urandom(24).hex(),
                    active=True,
                    is_confirmed=True,
                    confirmed_on=datetime.now(UTC),
                    created_at=datetime.now(UTC)
                )
                db.session.add(user)
            else:
                logger.info(f"Found existing user with ID: {user.id}")

            user.last_login_at = datetime.now(UTC)
            db.session.commit()
            logger.info("User transaction committed.")

            if user:
                login_user(user, remember=True)
                flash(f'Logged in successfully with Google!', 'success')
                return redirect(url_for("home.home"))
            return redirect(url_for("auth.login"))
        except Exception as e:
            logger.critical(f"UNCAUGHT EXCEPTION IN google_logged_in: {e}", exc_info=True)
            flash("An unexpected error occurred during login. Please try again.", "danger")
            return redirect(url_for("auth.login"))

    # Add similar handlers for Twitter and Facebook if needed
    return None  # No need to return an OAuth object