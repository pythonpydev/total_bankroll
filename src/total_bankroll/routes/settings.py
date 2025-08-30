from flask import Blueprint, render_template, redirect, request, url_for, flash, make_response, current_app
from flask_security import login_required, current_user, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Optional, Length
from ..extensions import db, mail, csrf
from ..models import User
from flask_security.utils import hash_password
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer
import os
from datetime import datetime

settings_bp = Blueprint("settings", __name__)

class UpdateEmailForm(FlaskForm):
    email = StringField('New Email', validators=[DataRequired(), Email()])
    submit_email = SubmitField('Save Email')

class UpdatePasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    submit_password = SubmitField('Save Password')

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

@settings_bp.route("/settings")
@login_required
def settings_page():
    """Settings page."""
    return render_template("settings.html")

@settings_bp.route("/delete_user_account")
@login_required
def delete_user_account():
    """Show confirmation dialog for deleting user account."""
    return render_template("confirm_delete_user_account.html")

@settings_bp.route("/delete_user_account_confirmed", methods=["POST"])
@login_required
@csrf.exempt
def delete_user_account_confirmed():
    """Deletes the user account."""
    try:
        user = current_user
        db.session.delete(user)
        db.session.commit()
        logout_user()
        flash("User account deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting user account: {e}", "danger")
    return redirect(url_for("auth.login"))

@settings_bp.route("/update_account_details")
@login_required
def update_account_details():
    email_form = UpdateEmailForm()
    password_form = UpdatePasswordForm()
    return render_template("update_account_details.html", email_form=email_form, password_form=password_form)

@settings_bp.route("/update_email", methods=['POST'])
@login_required
def update_email():
    email_form = UpdateEmailForm()
    if email_form.validate_on_submit():
        user = current_user
        new_email = email_form.email.data

        if new_email == user.email:
            flash('The new email address is the same as your current email address.', 'info')
            return redirect(url_for('settings.update_account_details'))

        # Check if the new email is already taken by another user
        existing_user = db.session.query(User).filter_by(email=new_email).first()
        if existing_user and existing_user.id != user.id:
            flash('This email address is already registered to another account.', 'danger')
            return redirect(url_for('settings.update_account_details'))

        # Send confirmation email
        token = generate_confirmation_token(new_email)
        confirm_url = url_for('settings.confirm_new_email', token=token, _external=True)
        msg = Message(
            'Confirm Your New Email',
            recipients=[new_email],
            body=f"Please click the link to confirm your email: {confirm_url}\nThis link expires in 1 hour."
        )
        try:
            mail.send(msg)
            flash('A confirmation email has been sent to your new email address. Please verify to update.', 'info')
        except Exception as e:
            flash(f'Failed to send confirmation email: {e}', 'danger')
    else:
        for field, errors in email_form.errors.items():
            for error in errors:
                flash(f"Error in {field}: {error}", 'danger')
    return redirect(url_for('settings.update_account_details'))

@settings_bp.route("/update_password", methods=['POST'])
@login_required
def update_password():
    password_form = UpdatePasswordForm()
    if password_form.validate_on_submit():
        user = current_user
        user.password_hash = hash_password(password_form.password.data)
        db.session.commit()
        flash('Your password has been updated successfully!', 'success')
    else:
        for field, errors in password_form.errors.items():
            for error in errors:
                flash(f"Error in {field}: {error}", 'danger')
    return redirect(url_for('settings.update_account_details'))

@settings_bp.route('/confirm_new_email/<token>')
@login_required
def confirm_new_email(token):
    email = confirm_token(token)
    if not email:
        flash('The confirmation link is invalid or has expired.', 'danger')
        return redirect(url_for('settings.settings_page'))

    user = current_user
    if user.email == email:
        flash('This is already your current email address.', 'info')
        return redirect(url_for('settings.settings_page'))

    # Check if the new email is already taken by another user
    existing_user = db.session.query(User).filter_by(email=email).first()
    if existing_user and existing_user.id != user.id:
        flash('This email address is already registered to another account.', 'danger')
        return redirect(url_for('settings.settings_page'))

    user.email = email
    user.is_confirmed = True # Mark as confirmed since they just confirmed new email
    user.confirmed_on = datetime.utcnow()
    db.session.commit()
    flash('Your email address has been updated and confirmed successfully!', 'success')
    return redirect(url_for('settings.settings_page'))
