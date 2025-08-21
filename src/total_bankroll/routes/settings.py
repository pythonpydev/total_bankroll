from flask import Blueprint, render_template, redirect, request, url_for, flash, make_response
from flask_security import login_required
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

            stream = io.StringIO(file.stream.read().decode("UTF8"))
            csv_reader = csv.reader(stream)

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
