from flask import Blueprint, render_template, redirect, request, url_for, flash
import psycopg2
import psycopg2.extras
from db import get_db
from datetime import datetime

settings_bp = Blueprint("settings", __name__)
reset_db_bp = Blueprint("delete_db", __name__, url_prefix="/settings")

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

@settings_bp.route("/settings")
def settings_page():
    """Settings page."""
    return render_template("settings.html")