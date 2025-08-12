from flask import Blueprint, render_template, redirect, request, url_for
import psycopg2
import psycopg2.extras
from db import get_db
from datetime import datetime

settings_bp = Blueprint("settings", __name__)

@settings_bp.route("/settings")
def settings_page():
    """Settings page."""
    return render_template("settings.html")

"""
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from total_bankroll.db import reset_db_data, init_db

settings_bp = Blueprint('settings', __name__, url_prefix='/settings')

@settings_bp.route('/reset_database', methods=['POST'])
def reset_database():
    if request.method == 'POST':
        try:
            reset_db_data()
            # Re-initialize the database schema after truncating data
            init_db(current_app)
            flash('Database reset successfully!', 'success')
        except Exception as e:
            flash(f'Error resetting database: {e}', 'danger')
    return redirect(url_for('settings.settings_page'))

@settings_bp.route('/')
def settings_page():
    return render_template('settings.html')
"""