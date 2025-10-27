from flask import Blueprint, render_template, redirect, request, url_for, flash, make_response, current_app, session
from flask_security import login_required, current_user, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, ValidationError, SelectField, FileField
from wtforms.validators import DataRequired, Email, EqualTo, Optional
from flask_wtf.file import FileRequired, FileAllowed
from ..extensions import mail, csrf
from ..models import db, User, OAuth, Sites, Assets, Deposits, Drawings, SiteHistory, AssetHistory
from flask_security.utils import hash_password
from flask_mail import Message 
from datetime import datetime, UTC
from ..utils import generate_token, confirm_token, is_email_taken, get_sorted_currencies
import re
import pyotp
import qrcode
import io
import base64
import json

settings_bp = Blueprint("settings", __name__)

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

class UpdateEmailForm(FlaskForm):
    email = StringField('New Email', validators=[DataRequired(), Email()])
    submit_email = SubmitField('Save Email')

class UpdatePasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired(), strong_password_check])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    submit_password = SubmitField('Save Password')

class UpdateDefaultCurrencyForm(FlaskForm):
    currency = SelectField('Default Currency', choices=[], validators=[DataRequired()])
    submit_currency = SubmitField('Save Default Currency')

class DeleteUserForm(FlaskForm):
    submit = SubmitField('Yes, delete my account')

class ResetDatabaseForm(FlaskForm):
    submit = SubmitField('Yes, reset my data')

class ExportDataForm(FlaskForm):
    submit = SubmitField('Export My Data')

class ImportDataForm(FlaskForm):
    data_file = FileField('JSON File', validators=[FileRequired(), FileAllowed(['json'], 'JSON files only!')])
    submit = SubmitField('Import My Data')

@settings_bp.route("/settings")
@login_required
def settings_page():
    """Settings page."""
    reset_database_form = ResetDatabaseForm()
    export_data_form = ExportDataForm()
    import_data_form = ImportDataForm()
    currency_form = UpdateDefaultCurrencyForm()
    currencies = get_sorted_currencies()
    currency_form.currency.choices = [(c['code'], c['name']) for c in currencies]
    if current_user.is_authenticated and hasattr(current_user, 'default_currency_code'):
        currency_form.currency.data = current_user.default_currency_code

    return render_template("settings.html", reset_database_form=reset_database_form, export_data_form=export_data_form, import_data_form=import_data_form, currency_form=currency_form, currencies=currencies)

@settings_bp.route('/settings/2fa/setup', methods=['GET', 'POST'])
@login_required
def setup_2fa():
    if current_user.otp_enabled:
        flash('2FA is already enabled.', 'info')
        return redirect(url_for('settings.settings_page'))

    if request.method == 'GET':
        # Generate a new secret if one doesn't exist in the session
        if 'otp_secret' not in session:
            session['otp_secret'] = pyotp.random_base32()

        # Generate QR code
        totp = pyotp.TOTP(session['otp_secret'])
        provisioning_uri = totp.provisioning_uri(name=current_user.email, issuer_name='StakeEasy.net')
        
        img = qrcode.make(provisioning_uri)
        buf = io.BytesIO()
        img.save(buf)
        buf.seek(0)
        qr_code_data = base64.b64encode(buf.getvalue()).decode('ascii')

        return render_template('setup_2fa.html', secret=session['otp_secret'], qr_code_data=qr_code_data)

    # Handle POST request for verification
    token = request.form.get('token')
    totp = pyotp.TOTP(session['otp_secret'])
    if totp.verify(token):
        current_user.otp_secret = session['otp_secret']
        current_user.otp_enabled = True
        db.session.commit()
        session.pop('otp_secret', None)
        flash('2FA has been successfully enabled!', 'success')
        return redirect(url_for('settings.settings_page'))
    else:
        flash('Invalid token. Please try again.', 'danger')
        # We need to regenerate the QR code data to re-render the page
        totp = pyotp.TOTP(session['otp_secret'])
        provisioning_uri = totp.provisioning_uri(name=current_user.email, issuer_name='StakeEasy.net')
        img = qrcode.make(provisioning_uri)
        buf = io.BytesIO()
        img.save(buf)
        buf.seek(0)
        qr_code_data = base64.b64encode(buf.getvalue()).decode('ascii')
        return render_template('setup_2fa.html', secret=session['otp_secret'], qr_code_data=qr_code_data)

@settings_bp.route('/settings/2fa/disable', methods=['GET'])
@login_required
def disable_2fa():
    if not current_user.otp_enabled:
        flash('2FA is not enabled.', 'info')
        return redirect(url_for('settings.settings_page'))

    current_user.otp_secret = None
    current_user.otp_enabled = False
    db.session.commit()
    flash('2FA has been disabled.', 'success')
    return redirect(url_for('settings.settings_page'))

@settings_bp.route("/delete_user_account")
@login_required
def delete_user_account():
    """Show confirmation dialog for deleting user account."""
    form = DeleteUserForm()
    return render_template("confirm_delete_user_account.html", form=form)

@settings_bp.route("/delete_user_account_confirmed", methods=["POST"])
@login_required
def delete_user_account_confirmed():
    """Deletes the user account."""
    form = DeleteUserForm()
    if form.validate_on_submit():
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
    
    flash("Invalid request. Please try again.", "danger")
    return redirect(url_for('settings.settings_page'))

@settings_bp.route("/reset_database", methods=["POST"])
@login_required
def reset_database():
    """Resets all user-specific data in the database."""
    form = ResetDatabaseForm()
    if form.validate_on_submit():
        try:
            user_id = current_user.id
            # Delete all data associated with the current user from relevant tables
            AssetHistory.query.filter_by(user_id=user_id).delete()
            SiteHistory.query.filter_by(user_id=user_id).delete()
            Deposits.query.filter_by(user_id=user_id).delete()
            Drawings.query.filter_by(user_id=user_id).delete()
            Assets.query.filter_by(user_id=user_id).delete()
            Sites.query.filter_by(user_id=user_id).delete()
            
            db.session.commit()
            flash("All your data has been reset successfully!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error resetting user data: {e}", "danger")
        return redirect(url_for('settings.settings_page'))
    flash("Invalid request. Please try again.", "danger")
    return redirect(url_for('settings.settings_page'))

@settings_bp.route("/export_data", methods=["GET"])
@login_required
def export_data():
    """Exports all user-specific data as a JSON file."""
    try:
        user_id = current_user.id
        user_data = {
            "user": {
                "id": current_user.id,
                "email": current_user.email,
                "default_currency_code": current_user.default_currency_code,
                "is_confirmed": current_user.is_confirmed,
                "confirmed_on": current_user.confirmed_on.isoformat() if current_user.confirmed_on else None,
                "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
                "last_login_at": current_user.last_login_at.isoformat() if current_user.last_login_at else None,
                "otp_enabled": current_user.otp_enabled
            },
            "sites": [],
            "assets": [],
            "deposits": [],
            "drawings": [],
            "site_history": [],
            "asset_history": []
        }

        # Fetch Sites
        for site in Sites.query.filter_by(user_id=user_id).all():
            user_data["sites"].append({
                "id": site.id,
                "name": site.name,
                "display_order": site.display_order
            })

        # Fetch Assets
        for asset in Assets.query.filter_by(user_id=user_id).all():
            user_data["assets"].append({
                "id": asset.id,
                "name": asset.name,
                "display_order": asset.display_order
            })

        # Fetch Deposits
        for deposit in Deposits.query.filter_by(user_id=user_id).all():
            user_data["deposits"].append({
                "id": deposit.id,
                "date": deposit.date.isoformat(),
                "amount": str(deposit.amount),
                "currency": deposit.currency,
                "last_updated": deposit.last_updated.isoformat()
            })

        # Fetch Drawings
        for drawing in Drawings.query.filter_by(user_id=user_id).all():
            user_data["drawings"].append({
                "id": drawing.id,
                "date": drawing.date.isoformat(),
                "amount": str(drawing.amount),
                "currency": drawing.currency,
                "last_updated": drawing.last_updated.isoformat()
            })

        # Fetch Site History
        for sh in SiteHistory.query.filter_by(user_id=user_id).all():
            user_data["site_history"].append({
                "id": sh.id,
                "site_id": sh.site_id,
                "amount": str(sh.amount),
                "currency": sh.currency,
                "recorded_at": sh.recorded_at.isoformat()
            })

        # Fetch Asset History
        for ah in AssetHistory.query.filter_by(user_id=user_id).all():
            user_data["asset_history"].append({
                "id": ah.id,
                "asset_id": ah.asset_id,
                "amount": str(ah.amount),
                "currency": ah.currency,
                "recorded_at": ah.recorded_at.isoformat()
            })
        
        response = make_response(json.dumps(user_data, indent=4))
        response.headers["Content-Disposition"] = "attachment; filename=total_bankroll_data.json"
        response.headers["Content-Type"] = "application/json"
        return response
    except Exception as e:
        flash(f"Error exporting data: {e}", "danger")
        return redirect(url_for('settings.settings_page'))

@settings_bp.route("/import_data", methods=["POST"])
@login_required
def import_data():
    """Imports user data from an uploaded JSON file."""
    form = ImportDataForm()
    if form.validate_on_submit():
        try:
            file = request.files['data_file']
            imported_data = json.load(file)
            user_id = current_user.id

            # Clear existing user data before import to prevent conflicts
            AssetHistory.query.filter_by(user_id=user_id).delete()
            SiteHistory.query.filter_by(user_id=user_id).delete()
            Deposits.query.filter_by(user_id=user_id).delete()
            Drawings.query.filter_by(user_id=user_id).delete()
            Assets.query.filter_by(user_id=user_id).delete()
            Sites.query.filter_by(user_id=user_id).delete()
            # OAuth.query.filter_by(user_id=user_id).delete() # Excluded as per user request
            db.session.flush() # Ensure deletions are processed before new insertions

            # Import Sites (and map old IDs to new IDs if necessary for history)
            old_site_id_map = {}
            for item in imported_data.get("sites", []):
                site = Sites(
                    name=item["name"],
                    display_order=item["display_order"],
                    user_id=user_id
                )
                db.session.add(site)
                db.session.flush() # Get the new ID
                old_site_id_map[item["id"]] = site.id
            
            # Import Assets (and map old IDs to new IDs if necessary for history)
            old_asset_id_map = {}
            for item in imported_data.get("assets", []):
                asset = Assets(
                    name=item["name"],
                    display_order=item["display_order"],
                    user_id=user_id
                )
                db.session.add(asset)
                db.session.flush() # Get the new ID
                old_asset_id_map[item["id"]] = asset.id

            # Import Deposits
            for item in imported_data.get("deposits", []):
                deposit = Deposits(
                    date=datetime.fromisoformat(item["date"]),
                    amount=item["amount"],
                    currency=item["currency"],
                    last_updated=datetime.fromisoformat(item["last_updated"]),
                    user_id=user_id
                )
                db.session.add(deposit)

            # Import Drawings
            for item in imported_data.get("drawings", []):
                drawing = Drawings(
                    date=datetime.fromisoformat(item["date"]),
                    amount=item["amount"],
                    currency=item["currency"],
                    last_updated=datetime.fromisoformat(item["last_updated"]),
                    user_id=user_id
                )
                db.session.add(drawing)

            # Import Site History
            for item in imported_data.get("site_history", []):
                # Use the new site_id if mapping was done
                new_site_id = old_site_id_map.get(item["site_id"], None)
                if new_site_id:
                    sh = SiteHistory(
                        site_id=new_site_id,
                        amount=item["amount"],
                        currency=item["currency"],
                        recorded_at=datetime.fromisoformat(item["recorded_at"]),
                        user_id=user_id
                    )
                    db.session.add(sh)
                else:
                    flash(f"Warning: Site history record with old site_id {item["site_id"]} could not be linked to a new site. Skipping.", "warning")

            # Import Asset History
            for item in imported_data.get("asset_history", []):
                # Use the new asset_id if mapping was done
                new_asset_id = old_asset_id_map.get(item["asset_id"], None)
                if new_asset_id:
                    ah = AssetHistory(
                        asset_id=new_asset_id,
                        amount=item["amount"],
                        currency=item["currency"],
                        recorded_at=datetime.fromisoformat(item["recorded_at"]),
                        user_id=user_id
                    )
                    db.session.add(ah)
                else:
                    flash(f"Warning: Asset history record with old asset_id {item["asset_id"]} could not be linked to a new asset. Skipping.", "warning")

            db.session.commit()
            flash("User data imported successfully!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error importing data: {e}", "danger")
        return redirect(url_for('settings.settings_page'))
    flash("Invalid request. Please try again.", "danger")
    return redirect(url_for('settings.settings_page'))

@settings_bp.route("/update_account_details")
@login_required
def update_account_details():
    email_form = UpdateEmailForm()
    password_form = UpdatePasswordForm()
    currency_form = UpdateDefaultCurrencyForm()
    reset_database_form = ResetDatabaseForm()
    export_data_form = ExportDataForm()
    import_data_form = ImportDataForm()

    # Populate currency choices and set the current default
    currencies = get_sorted_currencies()
    currency_form.currency.choices = [(c['code'], c['name']) for c in currencies]
    if current_user.is_authenticated and hasattr(current_user, 'default_currency_code'):
        currency_form.currency.data = current_user.default_currency_code

    return render_template("update_account_details.html", email_form=email_form, password_form=password_form, currency_form=currency_form, reset_database_form=reset_database_form, export_data_form=export_data_form, import_data_form=import_data_form)

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

        # Check if the new email is already taken
        if is_email_taken(new_email, user.id):
            flash('This email address is already registered to another account.', 'danger')
            return redirect(url_for('settings.update_account_details'))

        # Send confirmation email
        token = generate_token(new_email)
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

@settings_bp.route("/update_default_currency", methods=['POST'])
@login_required
def update_default_currency():
    currency_form = UpdateDefaultCurrencyForm()
    currencies = get_sorted_currencies()
    currency_form.currency.choices = [(c['code'], c['name']) for c in currencies]

    if currency_form.validate_on_submit():
        user = current_user
        user.default_currency_code = currency_form.currency.data
        db.session.commit()
        flash('Your default currency has been updated successfully!', 'success')
    else:
        for field, errors in currency_form.errors.items():
            for error in errors:
                flash(f"Error in {field}: {error}", 'danger')
    return redirect(url_for('settings.settings_page'))

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

    # Check if the new email is already taken
    if is_email_taken(email, user.id):
        flash('This email address is already registered to another account.', 'danger')
        return redirect(url_for('settings.settings_page'))

    user.email = email
    user.is_confirmed = True # Mark as confirmed since they just confirmed new email
    user.confirmed_on = datetime.now(UTC)
    db.session.commit()
    flash('Your email address has been updated and confirmed successfully!', 'success')
    return redirect(url_for('settings.settings_page'))
