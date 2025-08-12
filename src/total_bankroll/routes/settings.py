from flask import Blueprint, render_template, redirect, request, url_for, flash, make_response
import psycopg2
import psycopg2.extras
from ..db import get_db
from datetime import datetime
import io
import csv

settings_bp = Blueprint("settings", __name__)
reset_db_bp = Blueprint("delete_db", __name__, url_prefix="/settings")
export_db_bp = Blueprint("export_db", __name__, url_prefix="/settings")
import_db_bp = Blueprint("import_db", __name__, url_prefix="/settings")

@reset_db_bp.route("/confirm_reset_database", methods=["GET"])
def confirm_reset_database():
    """Show confirmation dialog for database reset."""
    return render_template("confirm_reset_database.html")

@reset_db_bp.route("/reset_database", methods=["POST"])
def reset_database():
    """Reset the database by truncating all tables."""
    if request.method == "POST":
        try:
            conn = get_db()
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            # Truncate all tables
            cur.execute("TRUNCATE TABLE sites, assets, deposits, drawings, currency RESTART IDENTITY CASCADE;")
            conn.commit()
            cur.close()
            flash("Database reset successfully!", "success")
        except Exception as e:
            flash(f"Error resetting database: {e}", "danger")
        finally:
            conn.close()
    return redirect(url_for("settings.settings_page"))

@export_db_bp.route("/confirm_export_database", methods=["GET"])
def confirm_export_database():
    """Show confirmation dialog for database export."""
    return render_template("confirm_export_database.html")

@export_db_bp.route("/export_database", methods=["POST"])
def export_database():
    """Export the database to a CSV file."""
    try:
        conn = get_db()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        tables = ["sites", "assets", "deposits", "drawings", "currency"]
        output = io.StringIO()
        writer = csv.writer(output)

        for table_name in tables:
            cur.execute(f"SELECT * FROM {table_name};")
            rows = cur.fetchall()

            if rows:
                # Write table name as a header
                writer.writerow([f"Table: {table_name}"])
                # Write headers
                writer.writerow(rows[0].keys())
                # Write data
                for row in rows:
                    writer.writerow(list(row.values()))
                writer.writerow([]) # Add an empty row for separation

        cur.close()
        conn.close()

        response = make_response(output.getvalue())
        response.headers["Content-Disposition"] = "attachment; filename=database_export.csv"
        response.headers["Content-type"] = "text/csv"
        return response

    except Exception as e:
        flash(f"Error exporting database: {e}", "danger")
        return redirect(url_for("settings.settings_page"))
    
@import_db_bp.route("/confirm_export_database", methods=["GET"])
def confirm_import_database():
    """Show confirmation dialog for database import."""
    return render_template("confirm_import_database.html")

@import_db_bp.route("/import_database", methods=["POST"])
def export_database():
    """Import CSV   file to the database file."""
    try:
        conn = get_db()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        tables = ["sites", "assets", "deposits", "drawings", "currency"]
        output = io.StringIO()
        writer = csv.writer(output)

        for table_name in tables:
            cur.execute(f"SELECT * FROM {table_name};")
            rows = cur.fetchall()

            if rows:
                # Write table name as a header
                writer.writerow([f"Table: {table_name}"])
                # Write headers
                writer.writerow(rows[0].keys())
                # Write data
                for row in rows:
                    writer.writerow(list(row.values()))
                writer.writerow([]) # Add an empty row for separation

        cur.close()
        conn.close()

        response = make_response(output.getvalue())
        response.headers["Content-Disposition"] = "attachment; filename=database_export.csv"
        response.headers["Content-type"] = "text/csv"
        return response

    except Exception as e:
        flash(f"Error exporting database: {e}", "danger")
        return redirect(url_for("settings.settings_page"))

@export_db_bp.route("/confirm_import_database", methods=["GET"])
def confirm_import_database():
    """Show confirmation dialog for database import."""
    return render_template("confirm_import_database.html")

@export_db_bp.route("/import_database", methods=["POST"])
def import_database():
    """Import data from a CSV file into the database."""
    if request.method == "POST":
        if 'file' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)
        if file and file.filename.endswith('.csv'):
            try:
                conn = get_db()
                cur = conn.cursor()
                
                # Read the CSV file
                stream = io.StringIO(file.stream.read().decode("UTF8"))
                csv_reader = csv.reader(stream)

                # Truncate all tables and restart identity before import
                cur.execute("TRUNCATE TABLE sites, assets, deposits, drawings, currency RESTART IDENTITY CASCADE;")
                conn.commit()

                current_table = None
                headers = []
                data_to_insert = []

                for row in csv_reader:
                    if not row:
                        continue # Skip empty rows

                    if row[0].startswith("Table:"):
                        # New table section
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
                
                # Insert data for the last table
                if current_table and data_to_insert:
                    insert_data_into_table(cur, current_table, headers, data_to_insert)

                conn.commit()
                cur.close()
                conn.close()

                # Re-insert initial currency data after import
                from total_bankroll.currency import insert_initial_currency_data
                from flask import current_app
                with current_app.app_context():
                    insert_initial_currency_data(current_app)

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

    # Skip importing into currency table, as it's handled by insert_initial_currency_data
    if table_name == "currency":
        return

    # Construct the INSERT statement
    columns = ", ".join([f'"{h}"' for h in headers]) # Quote column names for safety
    placeholders = ", ".join(["%s"] * len(headers))
    insert_sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

    for row_data in data:
        # Ensure row_data has the same number of elements as headers
        if len(row_data) == len(headers):
            try:
                cur.execute(insert_sql, row_data)
            except Exception as e:
                print(f"Error executing INSERT for {table_name} with data {row_data}: {e}") # Debugging: Keep this for now
        else:
            print(f"Skipping row due to column mismatch in table {table_name}: {row_data} (Expected {len(headers)} columns, got {len(row_data)}) ") # For debugging: Keep this for now

@settings_bp.route("/settings")
def settings_page():
    """Settings page."""
    return render_template("settings.html")