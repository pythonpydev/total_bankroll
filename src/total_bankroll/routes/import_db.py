from flask import Blueprint, render_template, redirect, request, url_for, flash, current_app, jsonify
from flask_security import login_required, current_user
from ..models import db, Sites, Assets, SiteHistory, AssetHistory, Deposits, Drawings, Currency
import io
import csv
from decimal import Decimal, InvalidOperation
from datetime import datetime

import_db_bp = Blueprint("import_db", __name__, url_prefix="/settings")

def parse_datetime(value):
    if not value or value == 'None':
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            pass
    current_app.logger.warning(f"Could not parse date: {value}")
    return None

@import_db_bp.route("/confirm_import_database", methods=["GET"])
@login_required
def confirm_import_database():
    """Show confirmation dialog for database import."""
    return render_template("confirmations/confirm_import_database.html")

@import_db_bp.route("/import_database", methods=["POST"])
@login_required
def import_database():
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file part in the request.'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected.'}), 400

    if file and file.filename.endswith('.csv'):
        try:
            user_id = current_user.id

            # ── Phase 1: Parse the entire CSV into a dict of table -> rows ──
            stream = io.StringIO(file.stream.read().decode("UTF8"))
            reader = csv.reader(stream)

            parsed_tables = {}  # {table_name: {'headers': [...], 'rows': [[...], ...]}}
            current_table = None
            headers = []
            for row in reader:
                if not row:
                    continue
                if row[0].startswith("Table: "):
                    current_table = row[0].replace("Table: ", "").strip()
                    headers = next(reader)
                    model = get_model_for_table(current_table)
                    if not model:
                        raise ValueError(f"Unknown table '{current_table}' in CSV file.")
                    parsed_tables[current_table] = {'headers': headers, 'rows': []}
                elif current_table and headers:
                    parsed_tables[current_table]['rows'].append(row)

            # ── Phase 2: Delete in FK-safe order ──
            # Children first (they reference parents via FK)
            db.session.query(SiteHistory).filter_by(user_id=user_id).delete()
            db.session.query(AssetHistory).filter_by(user_id=user_id).delete()
            db.session.query(Deposits).filter_by(user_id=user_id).delete()
            db.session.query(Drawings).filter_by(user_id=user_id).delete()
            db.session.query(Sites).filter_by(user_id=user_id).delete()
            db.session.query(Assets).filter_by(user_id=user_id).delete()
            # Note: Currency is NOT deleted — the users table references it
            # via default_currency_code FK. We upsert currency rows instead.
            db.session.commit()

            # ── Phase 3: Insert in FK-safe order ──
            # Currency first (deposits/drawings/history reference it)
            # Then sites/assets (history references them)
            # Then deposits/drawings
            # Then history tables
            import_order = [
                'currency',
                'sites', 'assets',
                'deposits', 'drawings',
                'site_history', 'asset_history',
            ]

            for table_name in import_order:
                if table_name not in parsed_tables:
                    continue

                model = get_model_for_table(table_name)
                tbl_headers = parsed_tables[table_name]['headers']

                for row in parsed_tables[table_name]['rows']:
                    row_data = {}
                    for i, header in enumerate(tbl_headers):
                        value = row[i] if i < len(row) and row[i] != 'None' and row[i] != '' else None

                        # Type conversion
                        if header in ['amount', 'rate', 'small_blind', 'big_blind', 'min_buy_in', 'max_buy_in']:
                            row_data[header] = Decimal(value) if value is not None else None
                        elif header in ['date', 'recorded_at', 'last_updated', 'updated_at', 'created_at', 'last_login_at', 'confirmed_on']:
                            row_data[header] = parse_datetime(value)
                        elif header in ['id', 'site_id', 'asset_id', 'user_id', 'display_order']:
                            row_data[header] = int(value) if value is not None else None
                        elif header in ['active', 'is_confirmed']:
                            row_data[header] = value.lower() == 'true' if value is not None else False
                        else:
                            row_data[header] = value

                    # Enforce user_id for user-specific tables
                    if hasattr(model, 'user_id'):
                        row_data['user_id'] = user_id

                    # Currency: upsert by code (can't DELETE due to users FK)
                    if model == Currency:
                        existing = db.session.query(Currency).filter_by(
                            code=row_data.get('code')
                        ).first()
                        if existing:
                            existing.name = row_data.get('name', existing.name)
                            existing.rate = row_data.get('rate', existing.rate)
                            existing.symbol = row_data.get('symbol', existing.symbol)
                            existing.updated_at = row_data.get('updated_at', existing.updated_at)
                        else:
                            obj = Currency(**row_data)
                            db.session.add(obj)
                    else:
                        obj = model(**row_data)
                        db.session.add(obj)

            db.session.commit()
            return jsonify({'success': True, 'message': 'Database imported successfully!'})
        except (ValueError, IndexError, InvalidOperation, Exception) as e:
            db.session.rollback()
            current_app.logger.error(f"Error importing database: {e}")
            return jsonify({'success': False, 'message': f'Error importing database: A problem occurred during the import process. Please ensure the CSV file format is correct. Error: {e}'}), 500
    else:
        return jsonify({'success': False, 'message': 'Invalid file type. Please upload a CSV file.'}), 400

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
