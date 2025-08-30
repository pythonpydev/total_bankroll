from flask import Blueprint, render_template, redirect, request, url_for, flash, jsonify
from flask_security import login_required, current_user
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
    """Reset the database by deleting all of the current user's data."""
    try:
        user_id = current_user.id
        # Delete user-specific data
        db.session.query(SiteHistory).filter_by(user_id=user_id).delete()
        db.session.query(AssetHistory).filter_by(user_id=user_id).delete()
        db.session.query(Sites).filter_by(user_id=user_id).delete()
        db.session.query(Assets).filter_by(user_id=user_id).delete()
        db.session.query(Deposits).filter_by(user_id=user_id).delete()
        db.session.query(Drawings).filter_by(user_id=user_id).delete()
        db.session.commit()
        return jsonify({'success': True, 'message': 'Your data has been reset successfully!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error resetting database: {e}'}), 500
