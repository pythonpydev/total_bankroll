from flask import Blueprint, render_template, redirect, request, url_for, flash
from flask_security import login_required
from ..extensions import db
from ..models import Sites, Assets, SiteHistory, AssetHistory, Deposits, Drawings

reset_db_bp = Blueprint("reset_db", __name__, url_prefix="/settings")

@reset_db_bp.route("/confirm_reset_database", methods=["GET"])
@login_required
def confirm_reset_database():
    """Show confirmation dialog for database reset."""
    return render_template("confirm_reset_database.html")

@reset_db_bp.route("/reset_database", methods=["POST"])
@login_required
def reset_database():
    """Reset the database by truncating all tables."""
    if request.method == "POST":
        try:
            # Truncate all tables except currency
            db.session.query(SiteHistory).delete()
            db.session.query(AssetHistory).delete()
            db.session.query(Sites).delete()
            db.session.query(Assets).delete()
            db.session.query(Deposits).delete()
            db.session.query(Drawings).delete()
            db.session.commit()
            flash("Database reset successfully!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error resetting database: {e}", "danger")
    return redirect(url_for("settings.settings_page"))
