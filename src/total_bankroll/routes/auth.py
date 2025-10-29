
from flask import Blueprint, render_template, redirect, url_for, flash, current_app, request, session
from flask_security import login_user, logout_user, login_required, current_user
from flask_security.utils import hash_password, verify_password
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Email, EqualTo
from ..extensions import mail
from ..models import db, User
from flask_mail import Message
import os
from sqlalchemy.exc import IntegrityError
from flask_dance.contrib.google import google as google_blueprint
from flask_dance.contrib.facebook import facebook as facebook_blueprint
from datetime import datetime, UTC
from ..utils import generate_token, confirm_token
import logging
import pyotp
import re

auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

def strong_password_check(form, field):
    """Custom validator for password strength."""
    password = field.data
    errors = []
    if len(password) < 8:
        errors.append("be at least 8 characters long")
    if not re.search(r"[a-z]", password):
        errors.append("contain at least one lowercase letter")
    if not re.search(r"[A-Z]", password):
        errors.append("contain at least one uppercase letter")
    if not re.search(r"\d", password):
        errors.append("contain at least one digit")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        errors.append("contain at least one special character")

    if errors:
        error_message = "Password must " + ", ".join(errors) + "."
        raise ValidationError(error_message)

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')

class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), strong_password_check, EqualTo('confirm_password', message='Passwords must match.')])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField('Register')

class ForgotPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Send Reset Link')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired(), strong_password_check])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

class Verify2FAForm(FlaskForm):
    token = StringField('2FA Token', validators=[DataRequired()])
    submit = SubmitField('Verify')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        session.pop('_flashes', None)
    form = LoginForm()
    logger.debug(f"Login attempt for email: {form.email.data if form.email.data else 'None'}")
    if not form.validate_on_submit():
        logger.debug(f"Form validation failed: {form.errors}")
        return render_template('security/login_user.html', form=form)

    user_datastore = current_app.extensions['security'].datastore
    try:
        user = user_datastore.find_user(email=form.email.data)
        logger.debug(f"User lookup result: {user}")
    except Exception as e:
        logger.error(f"User lookup failed for email: {form.email.data}, error: {str(e)}")
        flash('Server error during login. Please try again.', 'danger')
        return redirect(url_for('auth.login'))

    if not user or not user.password_hash or not verify_password(form.password.data, user.password_hash):
        logger.error(f"Invalid email or password for email: {form.email.data}")
        flash('Invalid email or password.', 'danger')
        return redirect(url_for('auth.login'))

    if not user.is_confirmed:
        logger.error(f"User not confirmed: {form.email.data}")
        flash('Please verify your email address before logging in.', 'danger')
        return redirect(url_for('auth.login'))

    if user.id is None:
        logger.error(f"No user ID for email: {form.email.data}")
        flash('Account error: No user ID. Please contact support.', 'danger')
        return redirect(url_for('auth.login'))

    if user.otp_enabled:
        session['2fa_user_id'] = user.id
        # Redirect to a new 2FA verification page
        return redirect(url_for('auth.verify_2fa'))

    try:
        user.last_login_at = datetime.now(UTC)
        db.session.commit()
        login_user(user)
        logger.debug(f"User logged in: {user.email}, session: {session}")
        flash('Logged in successfully!', 'success')
        return redirect(url_for('home.home'))
    except Exception as e:
        logger.error(f"Login error for {form.email.data}: {str(e)}")
        db.session.rollback()
        flash('Login failed due to server error.', 'danger')
        return redirect(url_for('auth.login'))

@auth_bp.route('/verify-2fa', methods=['GET', 'POST'])
def verify_2fa():
    if '2fa_user_id' not in session:
        return redirect(url_for('auth.login'))

    form = Verify2FAForm()
    if form.validate_on_submit():
        user = db.session.get(User, session['2fa_user_id'])
        if not user:
            flash('User not found. Please try logging in again.', 'danger')
            return redirect(url_for('auth.login'))

        token = form.token.data
        totp = pyotp.TOTP(user.otp_secret)
        if totp.verify(token):
            session.pop('2fa_user_id', None)
            login_user(user)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('home.home'))
        else:
            flash('Invalid 2FA token.', 'danger')
            return redirect(url_for('auth.verify_2fa'))
    return render_template('security/verify_2fa.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        session.pop('_flashes', None)
    form = RegisterForm()
    logger.debug(f"Register attempt for email: {form.email.data if form.email.data else 'None'}")
    if not form.validate_on_submit():
        logger.debug(f"Form validation failed: {form.errors}")
        return render_template('security/register_user.html', form=form)

    try:
        user = User(
            email=form.email.data,
            password_hash=hash_password(form.password.data),
            fs_uniquifier=os.urandom(24).hex(),
            active=True,
            is_confirmed=False,
            created_at=datetime.now(UTC)
        )
        db.session.add(user)
        db.session.commit()
        token = generate_token(user.email)
        confirm_url = url_for('auth.confirm_email', token=token, _external=True)
        msg = Message(
            'Confirm Your Email',
            recipients=[user.email],
            body=f"Please click the link to confirm your email: {confirm_url}\nThe link expires in 1 hour."
        )
        try:
            mail.send(msg)
            logger.debug(f"Confirmation email sent to {user.email}")
            flash('Registration successful! Please check your email to verify your account.', 'success')
        except Exception as e:
            logger.error(f"Failed to send confirmation email to {user.email}: {str(e)}")
            flash('Registration successful, but failed to send confirmation email. Please contact support.', 'warning')
        return redirect(url_for('auth.login'))
    except IntegrityError:
        db.session.rollback()
        logger.error(f"Email already exists during registration: {form.email.data}")
        flash('Email already exists. Please use a different email.', 'danger')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error during registration: {str(e)}")
        flash('Registration failed. Please try again.', 'danger')
    return render_template('security/register_user.html', form=form)

@auth_bp.route('/confirm/<token>')
def confirm_email(token):
    email = confirm_token(token)
    if not email:
        logger.error(f"Invalid or expired confirmation token: {token}")
        flash('The confirmation link is invalid or has expired.', 'danger')
        return redirect(url_for('auth.login'))
    user = db.session.query(User).filter_by(email=email).first()
    if user:
        if user.is_confirmed:
            logger.info(f"Account already confirmed for email: {email}")
            flash('Account already confirmed.', 'info')
        else:
            user.is_confirmed = True
            user.confirmed_on = datetime.now(UTC)
            try:
                db.session.commit()
                logger.debug(f"Email confirmed for {email}")
                flash('Email confirmed successfully! You can now log in.', 'success')
            except Exception as e:
                db.session.rollback()
                logger.error(f"Error during email confirmation for {email}: {str(e)}")
                flash('Error confirming email. Please try again.', 'danger')
    else:
        logger.error(f"User not found for confirmation: {email}")
        flash('User not found.', 'danger')
    return redirect(url_for('auth.login'))

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = db.session.query(User).filter_by(email=form.email.data).first()
        logger.debug(f"Forgot password user lookup for {form.email.data}: {user}")
        if user:
            token = generate_token(user.email)
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            msg = Message(
                'Reset Your Password',
                recipients=[user.email],
                html=render_template('security/reset_password_email.html', reset_url=reset_url)
            )
            try:
                mail.send(msg)
                logger.debug(f"Password reset email sent to {user.email}")
                flash('A password reset link has been sent to your email.', 'success')
            except Exception as e:
                logger.error(f"Failed to send password reset email to {user.email}: {str(e)}")
                flash('Failed to send password reset email. Please contact support.', 'warning')
            return redirect(url_for('auth.login'))
        else:
            logger.error(f"Email not found for password reset: {form.email.data}")
            flash('Email not found.', 'danger')
    return render_template('security/forgot_password.html', form=form)

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    email = confirm_token(token)
    if not email:
        logger.error(f"Invalid or expired reset token: {token}")
        flash('The reset link is invalid or has expired.', 'danger')
        return redirect(url_for('auth.login'))

    logger.info(f"Password reset attempt for email: {email}")

    user = db.session.query(User).filter_by(email=email).first()
    if not user:
        logger.error(f"User not found for reset: {email}")
        flash('User not found.', 'danger')
        return redirect(url_for('auth.login'))

    logger.info(f"User found for password reset: {user}")

    form = ResetPasswordForm()
    if form.validate_on_submit():
        try:
            user.password_hash = hash_password(form.password.data)
            logger.info(f"Password hash created for user: {user.email}")
            db.session.commit()
            logger.info(f"Password updated and committed for user: {user.email}")
            flash('Password reset successfully! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error during password reset for {user.email}: {str(e)}")
            flash('An error occurred during password reset. Please try again.', 'danger')

    return render_template('security/reset_password.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('_flashes', None)
    flash('Logged out successfully.', 'success')
    return redirect(url_for('auth.login'))
