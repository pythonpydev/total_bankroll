from flask import Blueprint, render_template, request, redirect, url_for, current_app, send_file, jsonify, flash
from flask_security import current_user
from ..extensions import db
from ..models import Sites, Assets, Drawings, Deposits, SiteHistory, AssetHistory, Currency
import csv
import io
from datetime import datetime

common_bp = Blueprint('common', __name__)

@common_bp.route('/confirm_delete/<item_type>/<int:item_id>')
def confirm_delete(item_type, item_id):
    return render_template('confirm_delete.html', item_type=item_type, item_id=item_id)

@common_bp.route('/perform_delete/<item_type>/<int:item_id>', methods=['POST'])
def perform_delete(item_type, item_id):
    try:
        if item_type == 'site':
            SiteHistory.query.filter_by(site_id=item_id, user_id=current_user.id).delete()
            Sites.query.filter_by(id=item_id, user_id=current_user.id).delete()
            db.session.commit()
            flash("Site deleted successfully!", "success")
            return redirect(url_for('poker_sites.poker_sites_page'))
        elif item_type == 'asset':
            AssetHistory.query.filter_by(asset_id=item_id, user_id=current_user.id).delete()
            Assets.query.filter_by(id=item_id, user_id=current_user.id).delete()
            db.session.commit()
            flash("Asset deleted successfully!", "success")
            return redirect(url_for('assets.assets_page'))
        elif item_type == 'withdrawal':
            Drawings.query.filter_by(id=item_id, user_id=current_user.id).delete()
            db.session.commit()
            flash("Withdrawal deleted successfully!", "success")
            return redirect(url_for('withdrawal.withdrawal'))
        elif item_type == 'deposit':
            Deposits.query.filter_by(id=item_id, user_id=current_user.id).delete()
            db.session.commit()
            flash("Deposit deleted successfully!", "success")
            return redirect(url_for('deposit.deposit'))
        else:
            flash("Invalid item type", "danger")
            return "Invalid item type", 400
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting record: {e}", "danger")
        return f"Error deleting record: {e}", 500

@common_bp.route('/perform_export_database', methods=['POST'])
def perform_export_database():
    try:
        tables = {
            'sites': Sites,
            'assets': Assets,
            'deposits': Deposits,
            'drawings': Drawings,
            'site_history': SiteHistory,
            'asset_history': AssetHistory,
            'currency': Currency # Include currency table
        }
        output = io.StringIO()
        writer = csv.writer(output)

        for table_name, model in tables.items():
            # Fetch data for the current user, or all data for Currency table
            if model == Currency:
                rows = db.session.query(model).all()
            else:
                rows = db.session.query(model).filter_by(user_id=current_user.id).all()

            if rows:
                # Write table name as a header
                writer.writerow([f"Table: {table_name}"])
                
                # Write headers
                # Get column names from the model's __table__.columns
                headers = [column.name for column in model.__table__.columns]
                writer.writerow(headers)
                
                # Write data rows
                for row in rows:
                    writer.writerow([getattr(row, header) for header in headers])
                writer.writerow([]) # Add an empty row for separation

        output.seek(0)
        return send_file(io.BytesIO(output.getvalue().encode('utf-8')), mimetype='text/csv', as_attachment=True, download_name='bankroll_export.csv')

    except Exception as e:
        current_app.logger.error(f"Error exporting database: {e}")
        flash(f"Error exporting database: {e}", "danger")
        return f"Error exporting database: {e}", 500

@common_bp.route('/perform_import_database', methods=['POST'])
def perform_import_database():
    if 'file' not in request.files:
        flash('No file part', 'danger')
        return redirect(url_for('settings.settings_page'))
    file = request.files['file']
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(url_for('settings.settings_page'))
    if file and file.filename.endswith('.csv'):
        try:
            # Clear existing user data before import
            db.session.query(SiteHistory).filter_by(user_id=current_user.id).delete()
            db.session.query(AssetHistory).filter_by(user_id=current_user.id).delete()
            db.session.query(Deposits).filter_by(user_id=current_user.id).delete()
            db.session.query(Drawings).filter_by(user_id=current_user.id).delete()
            db.session.query(Sites).filter_by(user_id=current_user.id).delete()
            db.session.query(Assets).filter_by(user_id=current_user.id).delete()
            db.session.commit()

            stream = io.StringIO(file.stream.read().decode("UTF8"))
            reader = csv.reader(stream)

            current_table = None
            headers = []
            for row in reader:
                if not row: # Skip empty rows
                    continue
                if row[0].startswith("Table: "):
                    current_table = row[0].replace("Table: ", "").strip()
                    headers = next(reader) # Read headers for the current table
                    model = get_model_for_table(current_table)
                    if not model:
                        flash(f"Unknown table '{current_table}' in CSV file.", "danger")
                        return redirect(url_for('settings.settings_page'))
                elif current_table and headers: # Data rows
                    row_data = {}
                    for i, header in enumerate(headers):
                        if header.strip(): # Only process non-empty headers
                            value = row[i] if i < len(row) else None
                            # Convert types if necessary (e.g., 'True'/'False' to boolean, numbers to Decimal)
                            if header in ['amount', 'deposited_at', 'withdrawn_at', 'rate', 'small_blind', 'big_blind', 'min_buy_in', 'max_buy_in']:
                                row_data[header] = Decimal(value) if value else Decimal(0)
                            elif header in ['date', 'recorded_at', 'last_updated', 'confirmed_on', 'created_at', 'last_login_at']:
                                row_data[header] = datetime.strptime(value, "%Y-%m-%d %H:%M:%S.%f") if value else None
                            elif header in ['active', 'is_confirmed']:
                                row_data[header] = value.lower() == 'true' if value else False
                            else:
                                row_data[header] = value

                    # Add user_id if not present and not currency table
                    if 'user_id' not in row_data and model != Currency:
                        row_data['user_id'] = current_user.id
                    elif 'user_id' in row_data and model != Currency:
                        # Ensure imported user_id matches current_user.id
                        if row_data['user_id'] != current_user.id:
                            current_app.logger.warning(f"Skipping row for table {current_table} due to user_id mismatch: {row_data}")
                            continue # Skip this row if user_id doesn't match

                    obj = model(**row_data)
                    db.session.add(obj)

            db.session.commit()
            flash("Database imported successfully!", "success")
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error importing database: {e}")
            flash(f"Error importing database: {e}", "danger")
    else:
        flash('Invalid file type. Please upload a CSV file.', 'danger')
    return redirect(url_for("settings.settings_page"))

def get_model_for_table(table_name):
    if table_name == 'sites':
        return Sites
    elif table_name == 'assets':
        return Assets
    elif table_name == 'deposits':
        return Deposits
    elif table_name == 'drawings':
        return Drawings
    elif table_name == 'site_history':
        return SiteHistory
    elif table_name == 'asset_history':
        return AssetHistory
    elif table_name == 'currency':
        return Currency
    else:
        return None
