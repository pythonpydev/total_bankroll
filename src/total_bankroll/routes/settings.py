from flask import Blueprint, render_template, redirect, request, url_for, flash, make_response, current_app
from flask_security import login_required, current_user, logout_user
from ..db import get_db
from datetime import datetime
import io
import csv
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Optional, Length
from total_bankroll.extensions import db, mail, csrf
from ..models import User
from flask_security.utils import hash_password
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer
import os

settings_bp = Blueprint("settings", __name__)
reset_db_bp = Blueprint("delete_db", __name__, url_prefix="/settings")
export_db_bp = Blueprint("export_db", __name__, url_prefix="/settings")
import_db_bp = Blueprint("import_db", __name__, url_prefix="/settings")

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

@reset_db_bp.route("/confirm_reset_database", methods=["GET"])
def confirm_reset_database():
    """Show confirmation dialog for database reset."""
    return render_template("confirm_reset_database.html")

@reset_db_bp.route("/reset_database", methods=["POST"])
def reset_database():
    """Reset the database by truncating all tables."""
    if request.method == "POST":
        conn = None
        try:
            conn = get_db()
            cur = conn.cursor()
            # Truncate all tables except currency
            cur.execute("TRUNCATE TABLE sites;")
            cur.execute("ALTER TABLE sites AUTO_INCREMENT = 1;")
            cur.execute("TRUNCATE TABLE assets;")
            cur.execute("ALTER TABLE assets AUTO_INCREMENT = 1;")
            cur.execute("TRUNCATE TABLE deposits;")
            cur.execute("ALTER TABLE deposits AUTO_INCREMENT = 1;")
            cur.execute("TRUNCATE TABLE drawings;")
            cur.execute("ALTER TABLE drawings AUTO_INCREMENT = 1;")
            conn.commit()
            cur.close()
            flash("Database reset successfully!", "success")
        except Exception as e:
            flash(f"Error resetting database: {e}", "danger")
        finally:
            if conn:
                conn.close()
    return redirect(url_for("settings.settings_page"))

@export_db_bp.route("/confirm_export_database", methods=["GET"])
def confirm_export_database():
    """Show confirmation dialog for database export."""
    return render_template("confirm_export_database.html")

@export_db_bp.route("/export_database", methods=["POST"])
def export_database():
    """Export the database to a CSV file."""
    conn = None
    try:
        conn = get_db()
        cur = conn.cursor()

        tables = ["sites", "assets", "deposits", "drawings", "currency"]
        output = io.StringIO()
        writer = csv.writer(output)

        for table_name in tables:
            cur.execute(f"SELECT * FROM {table_name};")
            rows = cur.fetchall()

            if rows:
                writer.writerow([f"Table: {table_name}"])
                writer.writerow(rows[0].keys())
                for row in rows:
                    writer.writerow(list(row.values()))
                writer.writerow([])

        cur.close()

        response = make_response(output.getvalue())
        response.headers["Content-Disposition"] = "attachment; filename=database_export.csv"
        response.headers["Content-type"] = "text/csv"
        return response

    except Exception as e:
        flash(f"Error exporting database: {e}", "danger")
        return redirect(url_for("settings.settings_page"))
    finally:
        if conn:
            conn.close()

@import_db_bp.route("/confirm_import_database", methods=["GET"])
def confirm_import_database():
    """Show confirmation dialog for database import."""
    return render_template("confirm_import_database.html")

@import_db_bp.route("/import_database", methods=["POST"])
def import_database():
    """Import data from a CSV file into the database."""
    if 'file' not in request.files:
        flash('No file part', 'danger')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(request.url)
    if file and file.filename.endswith('.csv'):
        conn = None
        try:
            conn = get_db()
            cur = conn.cursor()

            cur.execute("SET FOREIGN_KEY_CHECKS = 0;")
            cur.execute("TRUNCATE TABLE sites;")
            cur.execute("ALTER TABLE sites AUTO_INCREMENT = 1;")
            cur.execute("TRUNCATE TABLE assets;")
            cur.execute("ALTER TABLE assets AUTO_INCREMENT = 1;")
            cur.execute("TRUNCATE TABLE deposits;")
            cur.execute("ALTER TABLE deposits AUTO_INCREMENT = 1;")
            cur.execute("TRUNCATE TABLE drawings;")
            cur.execute("ALTER TABLE drawings AUTO_INCREMENT = 1;")
            cur.execute("TRUNCATE TABLE currency;")
            cur.execute("ALTER TABLE currency AUTO_INCREMENT = 1;")
            cur.execute("SET FOREIGN_KEY_CHECKS = 1;")
            conn.commit()

            stream = io.StringIO(file.stream.read().decode("UTF8"))
            csv_reader = csv.reader(stream)

            current_table = None
            headers = []
            data_to_insert = [] # Initialize data_to_insert here

            for row in csv_reader:
                # Skip completely empty rows or rows with only commas
                if not any(field.strip() for field in row):
                    continue

                if row[0].startswith("Table:"):
                    # If we were processing a table, insert its data
                    if current_table and data_to_insert:
                        insert_data_into_table(cur, current_table, headers, data_to_insert)
                        data_to_insert = [] # Reset for next table

                    current_table = row[0].split(":")[1].strip()
                    headers = [] # Reset headers for new table
                elif current_table and not headers:
                    # This is the header row for the current table
                    headers = row
                elif current_table:
                    # This is a data row
                    data_to_insert.append(row)

            # Insert data for the last table after the loop finishes
            if current_table and data_to_insert:
                insert_data_into_table(cur, current_table, headers, data_to_insert)

            conn.commit()
            cur.close()
            flash("Database imported successfully!", "success")
        except Exception as e:
            flash(f"Error importing database: {e}", "danger")
        finally:
            if conn:
                conn.close()
    else:
        flash('Invalid file type. Please upload a CSV file.', 'danger')
    return redirect(url_for("settings.settings_page"))

def insert_data_into_table(cur, table_name, headers, data):
    if not headers or not data:
        return

    # Filter out empty headers
    valid_headers = [h for h in headers if h.strip()]
    if not valid_headers: # If no valid headers, return
        return

    columns = ", ".join([f'`{h}`' for h in valid_headers])
    placeholders = ", ".join(["%s"] * len(valid_headers))
    insert_sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

    for row_data in data:
        # Filter out empty fields from row_data corresponding to valid headers
        filtered_row_data = [field for i, field in enumerate(row_data) if i < len(headers) and headers[i].strip()]

        if len(filtered_row_data) == len(valid_headers):
            try:
                cur.execute(insert_sql, filtered_row_data)
            except Exception as e:
                current_app.logger.error(f"Error executing INSERT for {table_name} with data {row_data}: {e}")
        else:
            print(f"Skipping row due to column mismatch in table {table_name}: {row_data} (Expected {len(valid_headers)} columns, got {len(filtered_row_data)}) ")

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