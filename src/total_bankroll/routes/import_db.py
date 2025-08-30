from flask import Blueprint, render_template, redirect, request, url_for, flash, current_app
from flask_security import login_required
from ..extensions import db
from ..models import Sites, Assets, SiteHistory, AssetHistory, Deposits, Drawings, Currency
import io
import csv

import_db_bp = Blueprint("import_db", __name__, url_prefix="/settings")

@import_db_bp.route("/confirm_import_database", methods=["GET"])
@login_required
def confirm_import_database():
    """Show confirmation dialog for database import."""
    return render_template("confirm_import_database.html")

@import_db_bp.route("/import_database", methods=["POST"])
@login_required
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
        try:
            # Truncate all tables
            db.session.query(SiteHistory).delete()
            db.session.query(AssetHistory).delete()
            db.session.query(Sites).delete()
            db.session.query(Assets).delete()
            db.session.query(Deposits).delete()
            db.session.query(Drawings).delete()
            db.session.query(Currency).delete()
            db.session.commit()

            stream = io.StringIO(file.stream.read().decode("UTF8"))
            csv_reader = csv.reader(stream)

            current_table = None
            headers = []
            for row in csv_reader:
                if not any(field.strip() for field in row):
                    continue

                if row[0].startswith("Table:"):
                    current_table = row[0].split(":")[1].strip()
                    headers = next(csv_reader)
                    model = get_model_for_table(current_table)
                    if not model:
                        flash(f"Unknown table '{current_table}' in CSV file.", "danger")
                        return redirect(url_for("settings.settings_page"))
                elif current_table and headers:
                    row_data = {header: (val if val else None) for header, val in zip(headers, row)}
                    obj = model(**row_data)
                    db.session.add(obj)

            db.session.commit()
            flash("Database imported successfully!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error importing database: {e}", "danger")
    else:
        flash('Invalid file type. Please upload a CSV file.', 'danger')
    return redirect(url_for("settings.settings_page"))

def get_model_for_table(table_name):
    if table_name == 'sites':
        return Sites
    elif table_name == 'assets':
        return Assets
    elif table_name == 'site_history':
        return SiteHistory
    elif table_name == 'asset_history':
        return AssetHistory
    elif table_name == 'deposits':
        return Deposits
    elif table_name == 'drawings':
        return Drawings
    elif table_name == 'currency':
        return Currency
    else:
        return None
