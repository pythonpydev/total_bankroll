from flask import Blueprint, render_template, request, redirect, url_for, current_app, send_file
from flask_security import current_user
from ..db import get_db, init_db_tables
import csv
import io

common_bp = Blueprint('common', __name__)

@common_bp.route('/confirm_delete/<item_type>/<int:item_id>')
def confirm_delete(item_type, item_id):
    return render_template('confirm_delete.html', item_type=item_type, item_id=item_id)

@common_bp.route('/perform_delete/<item_type>/<int:item_id>', methods=['POST'])
def perform_delete(item_type, item_id):
    conn = get_db()
    cur = conn.cursor()
    try:
        if item_type == 'site':
            cur.execute("DELETE FROM sites WHERE id = %s AND user_id = %s", (item_id, current_user.id))
            conn.commit()
            return redirect(url_for('poker_sites.poker_sites_page'))
        elif item_type == 'asset':
            cur.execute("DELETE FROM assets WHERE id = %s AND user_id = %s", (item_id, current_user.id))
            conn.commit()
            return redirect(url_for('assets.assets_page'))
        elif item_type == 'withdrawal':
            cur.execute("DELETE FROM drawings WHERE id = %s AND user_id = %s", (item_id, current_user.id))
            conn.commit()
            return redirect(url_for('withdrawal.withdrawal'))
        elif item_type == 'deposit':
            cur.execute("DELETE FROM deposits WHERE id = %s AND user_id = %s", (item_id, current_user.id))
            conn.commit()
            return redirect(url_for('deposit.deposit'))
        else:
            return "Invalid item type", 400
    except Exception as e:
        conn.rollback()
        return f"Error deleting record: {e}", 500
    finally:
        cur.close()
        # conn.close() # Handled by teardown_appcontext

@common_bp.route('/confirm_reset_database')
def confirm_reset_database():
    return render_template('confirm_reset_database.html')

@common_bp.route('/perform_reset_database', methods=['POST'])
def perform_reset_database():
    conn = get_db()
    cur = conn.cursor()
    try:
        # Drop all tables
        cur.execute("SET FOREIGN_KEY_CHECKS = 0")
        cur.execute("SHOW TABLES")
        tables = cur.fetchall()
        for table in tables:
            table_name = list(table.values())[0] # Get the table name from the dictionary
            cur.execute(f"DROP TABLE IF EXISTS `{table_name}`")
        cur.execute("SET FOREIGN_KEY_CHECKS = 1")
        conn.commit()

        # Reinitialize tables
        init_db_tables(conn, current_app._get_current_object()) # Pass current_app object
        conn.commit()

        return redirect(url_for('home.home')) # Redirect to home page after reset
    except Exception as e:
        conn.rollback()
        return f"Error resetting database: {e}", 500
    finally:
        cur.close()
        # conn.close() # Handled by teardown_appcontext

@common_bp.route('/confirm_export_database')
def confirm_export_database():
    return render_template('confirm_export_database.html')

@common_bp.route('/perform_export_database', methods=['POST'])
def perform_export_database():
    conn = get_db()
    cur = conn.cursor()
    try:
        tables = ['assets', 'deposits', 'drawings', 'sites'] # Tables to export
        output = io.BytesIO() # Changed to BytesIO
        text_wrapper = io.TextIOWrapper(output, encoding='utf-8', newline='') # Store TextIOWrapper
        writer = csv.writer(text_wrapper) # Pass TextIOWrapper to csv.writer

        for table_name in tables:
            cur.execute(f"SELECT * FROM {table_name} WHERE user_id = %s", (current_user.id,))
            rows = cur.fetchall()
            if rows:
                # Write table name as a header
                writer.writerow([f"Table: {table_name}"])
                # Write headers
                writer.writerow(rows[0].keys())
                # Write data rows
                for row in rows:
                    writer.writerow(row.values())
                writer.writerow([]) # Add an empty row for separation

        text_wrapper.flush() # Flush the TextIOWrapper
        text_wrapper.detach() # Detach the BytesIO object from the TextIOWrapper
        output.seek(0) # Seek to the beginning of the BytesIO object
        return send_file(output, mimetype='text/csv', as_attachment=True, download_name='bankroll_export.csv')

    except Exception as e:
        conn.rollback()
        return f"Error exporting database: {e}", 500
    finally:
        cur.close()

@common_bp.route('/confirm_import_database')
def confirm_import_database():
    return render_template('confirm_import_database.html')

@common_bp.route('/perform_import_database', methods=['POST'])
def perform_import_database():
    # This is a simplified import. A robust import would need more error handling,
    # transaction management, and careful parsing of the CSV to match table schemas.
    # It also assumes the CSV is well-formed and matches the expected structure.
    if 'file' not in request.files:
        return "No file part", 400
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400
    if file:
        conn = get_db()
        cur = conn.cursor()
        try:
            # Clear existing user data before import (optional, but safer for simple import)
            cur.execute("DELETE FROM assets WHERE user_id = %s", (current_user.id,))
            cur.execute("DELETE FROM deposits WHERE user_id = %s", (current_user.id,))
            cur.execute("DELETE FROM drawings WHERE user_id = %s", (current_user.id,))
            cur.execute("DELETE FROM sites WHERE user_id = %s", (current_user.id,))
            conn.commit()

            stream = io.StringIO(file.stream.read().decode("UTF8"))
            reader = csv.reader(stream)

            current_table = None
            headers = []
            for row in reader:
                if not row: # Skip empty rows
                    continue
                if row[0].startswith("Table: "):
                    current_table = row[0].replace("Table: ", "").strip()
                    headers = [] # Reset headers for new table
                elif current_table and not headers: # Next row after "Table:" should be headers
                    headers = row
                elif current_table and headers: # Data rows
                    # This part needs to be highly dynamic and careful with data types
                    # For simplicity, assuming all values can be inserted as strings/numbers directly
                    # In a real app, you'd map headers to columns and convert types
                    if current_table == 'assets':
                        # Assuming order: id, name, amount, last_updated, currency, user_id
                        # We will ignore id from CSV and let DB auto-increment
                        # We will use current_user.id for user_id
                        cur.execute(f"INSERT INTO assets (name, amount, last_updated, currency, user_id) VALUES (%s, %s, %s, %s, %s)",
                                    (row[1], row[2], row[3], row[4], current_user.id))
                    elif current_table == 'deposits':
                        # Assuming order: id, date, amount, deposited_at, last_updated, currency, user_id
                        cur.execute(f"INSERT INTO deposits (date, amount, deposited_at, last_updated, currency, user_id) VALUES (%s, %s, %s, %s, %s, %s)",
                                    (row[1], row[2], row[3], row[4], row[5], current_user.id))
                    elif current_table == 'drawings':
                        # Assuming order: id, date, amount, withdrawn_at, last_updated, currency, user_id
                        cur.execute(f"INSERT INTO drawings (date, amount, withdrawn_at, last_updated, currency, user_id) VALUES (%s, %s, %s, %s, %s, %s)",
                                    (row[1], row[2], row[3], row[4], row[5], current_user.id))
                    elif current_table == 'sites':
                        # Assuming order: id, name, amount, last_updated, currency, user_id
                        cur.execute(f"INSERT INTO sites (name, amount, last_updated, currency, user_id) VALUES (%s, %s, %s, %s, %s)",
                                    (row[1], row[2], row[3], row[4], current_user.id))
            conn.commit()
            return redirect(url_for('home.home'))
        except Exception as e:
            conn.rollback()
            return f"Error importing database: {e}", 500
        finally:
            cur.close()
    return "File upload failed", 400