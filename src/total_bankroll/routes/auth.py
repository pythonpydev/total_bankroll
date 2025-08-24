from flask import Blueprint, render_template, redirect, url_for, flash, current_app, request, session
from flask_security import login_user, logout_user, login_required, current_user
from flask_security.utils import hash_password, verify_password
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo
from itsdangerous import URLSafeTimedSerializer
from ..extensions import db, mail
from ..models import User
from flask_mail import Message
import os
from sqlalchemy.exc import IntegrityError
from flask_dance.contrib.google import google as google_blueprint
from flask_dance.contrib.facebook import facebook
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')

class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Register')

class ForgotPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Send Reset Link')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=current_app.config['SECURITY_PASSWORD_SALT'])

def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt=current_app.config['SECURITY_PASSWORD_SALT'],
            max_age=expiration
        )
        return email
    except Exception as e:
        current_app.logger.error(f"Error confirming token: {str(e)}")
        return False

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        flash('POST request received!', 'success')
        return redirect(url_for('auth.login'))
    return render_template('security/login_user.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if request.method == 'GET':
        session.pop('_flashes', None)
    if form.validate_on_submit():
        try:
            # Create user and commit to database
            user = User(
                email=form.email.data,
                password_hash=hash_password(form.password.data),
                fs_uniquifier=os.urandom(24).hex(),
                active=True,
                created_at=datetime.utcnow(),
                last_login_at=None,
                is_confirmed=False
            )
            db.session.add(user)
            db.session.commit()
            
            # Send confirmation email
            token = generate_confirmation_token(user.email)
            confirm_url = url_for('auth.confirm_email', token=token, _external=True)
            msg = Message(
                'Confirm Your Email',
                recipients=[user.email],
                body=f"Please click the link to confirm your email: {confirm_url}\nThe link expires in 1 hour."
            )
            try:
                mail.send(msg)
                flash('Registration successful! Please check your email to verify your account.', 'success')
            except Exception as e:
                current_app.logger.error(f"Failed to send confirmation email to {user.email}: {str(e)}")
                flash('Registration successful, but failed to send confirmation email. Please contact support.', 'warning')
            return redirect(url_for('auth.login'))
        except IntegrityError as e:
            db.session.rollback()
            current_app.logger.error(f"Database integrity error: {str(e)}")
            flash('Email already exists. Please use a different email.', 'danger')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error during registration: {str(e)}")
            flash('Registration failed. Please try again.', 'danger')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in {field}: {error}", 'danger')
    return render_template('security/register_user.html', form=form)

@auth_bp.route('/confirm/<token>')
def confirm_email(token):
    email = confirm_token(token)
    if not email:
        flash('The confirmation link is invalid or has expired.', 'danger')
        return redirect(url_for('auth.login'))
    user = db.session.query(User).filter_by(email=email).first()
    if user:
        if user.is_confirmed:
            flash('Account already confirmed.', 'info')
        else:
            user.is_confirmed = True
            user.confirmed_on = datetime.utcnow()
            db.session.commit()
            flash('Email confirmed successfully! You can now log in.', 'success')
    else:
        flash('User not found.', 'danger')
    return redirect(url_for('auth.login'))

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = db.session.query(User).filter_by(email=form.email.data).first()
        if user:
            token = generate_confirmation_token(user.email)
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            msg = Message(
                'Reset Your Password',
                recipients=[user.email],
                html=render_template('reset_password_email.html', reset_url=reset_url)
            )
            try:
                mail.send(msg)
                flash('A password reset link has been sent to your email.', 'success')
            except Exception as e:
                current_app.logger.error(f"Failed to send password reset email to {user.email}: {str(e)}")
                flash('Failed to send password reset email. Please contact support.', 'warning')
            return redirect(url_for('auth.login'))
        else:
            flash('Email not found.', 'danger')
    return render_template('security/forgot_password.html', form=form)

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    email = confirm_token(token)
    if not email:
        flash('The reset link is invalid or has expired.', 'danger')
        return redirect(url_for('auth.login'))
    
    current_app.logger.info(f"Password reset attempt for email: {email}")
    
    user = db.session.query(User).filter_by(email=email).first()
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('auth.login'))
        
    current_app.logger.info(f"User found for password reset: {user}")

    form = ResetPasswordForm()
    if form.validate_on_submit():
        try:
            user.password_hash = hash_password(form.password.data)
            current_app.logger.info("Password hash created for user: %s", user.email)
            db.session.commit()
            current_app.logger.info("Password updated and committed for user: %s", user.email)
            flash('Password reset successfully! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error during password reset for {user.email}: {e}")
            flash('An error occurred during password reset. Please try again.', 'danger')
            
    return render_template('security/reset_password.html', form=form)

@auth_bp.route('/google')
def google():
    return redirect(url_for('google.login'))


@auth_bp.route('/google/authorized')
def google_authorized():
    if not google_blueprint.authorized:
        flash("Google login failed.", "danger")
        return redirect(url_for("auth.login"))

    resp = google_blueprint.get("/oauth2/v2/userinfo")
    if not resp.ok:
        flash("Failed to fetch user info from Google.", "danger")
        return redirect(url_for("auth.login"))

    info = resp.json()
    email = info.get("email")
    if not email:
        flash("Email not provided by Google.", 'danger')
        return redirect(url_for("auth.login"))

    user = db.session.query(User).filter_by(email=email).first()
    if not user:
        user = User(
            email=email,
            is_confirmed=True,
            confirmed_on=datetime.utcnow(),
            fs_uniquifier=os.urandom(24).hex(),
            active=True,
            created_at=datetime.utcnow()
        )
        db.session.add(user)
        db.session.commit()

    login_user(user)
    flash("Logged in with Google successfully!", "success")
    return redirect(url_for('home.home'))

@auth_bp.route('/twitter')
def twitter():
    flash('Twitter login is not enabled.', 'danger')
    return redirect(url_for('auth.login'))

@auth_bp.route('/twitter/authorized')
def twitter_auth():
    flash('Twitter login is not enabled.', 'danger')
    return redirect(url_for('auth.login'))

@auth_bp.route('/facebook')
def facebook():
    if not os.getenv('FACEBOOK_CLIENT_ID') or not os.getenv('FACEBOOK_CLIENT_SECRET'):
        flash('Facebook login is not enabled.', 'danger')
        return redirect(url_for('auth.login'))
    if not facebook.authorized:
        return redirect(url_for('facebook.login'))
    return redirect(url_for('home.home'))

@auth_bp.route('/facebook/authorized')
def facebook_auth():
    if facebook.authorized:
        flash('Logged in with Facebook successfully!', 'success')
        return redirect(url_for('home.home'))
    flash('Facebook login failed.', 'danger')
    return redirect(url_for('auth.login'))

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('_flashes', None)
    flash('Logged out successfully.', 'success')
    return redirect(url_for('auth.login'))