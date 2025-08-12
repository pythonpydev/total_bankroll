from flask import Blueprint, render_template, redirect, request, url_for, flash, make_response
import psycopg2
import psycopg2.extras
from db import get_db
from datetime import datetime
import io
import csv

settings_bp = Blueprint("settings", __name__)
reset_db_bp = Blueprint("delete_db", __name__, url_prefix="/settings")
export_db_bp = Blueprint("export_db", __name__, url_prefix="/settings")

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

@settings_bp.route("/settings")
def settings_page():
    """Settings page."""
    return render_template("settings.html")