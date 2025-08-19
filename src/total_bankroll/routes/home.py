from flask import Blueprint, render_template
import pymysql

from ..db import get_db

home_bp = Blueprint("home", __name__)

@home_bp.route("/")
def home():
    """Main page."""
    conn = get_db()
    # NEW (PyMySQL):
    cur = conn.cursor()

    # Get current and previous poker site totals
    cur.execute("""
        WITH RankedSites AS (
            SELECT
                name,
                amount,
                last_updated,
                currency,
                ROW_NUMBER() OVER (PARTITION BY name ORDER BY last_updated DESC) as rn
            FROM sites
        ),
        ConvertedSites AS (
            SELECT
                rs.name,
                rs.amount / c.rate AS amount_usd,
                rs.rn
            FROM RankedSites rs
            JOIN currency c ON rs.currency = c.name
        )
        SELECT
            SUM(CASE WHEN rn = 1 THEN amount_usd ELSE 0 END) AS current_total,
            SUM(CASE WHEN rn = 2 THEN amount_usd ELSE 0 END) AS previous_total
        FROM ConvertedSites;
    """)
    poker_sites_data = cur.fetchone()

    current_poker_total = float(poker_sites_data['current_total']) if poker_sites_data and poker_sites_data['current_total'] is not None else 0.0
    previous_poker_total = float(poker_sites_data['previous_total']) if poker_sites_data and poker_sites_data['previous_total'] is not None else 0.0

    # Get current and previous asset totals
    cur.execute("""
        WITH RankedAssets AS (
            SELECT
                name,
                amount,
                last_updated,
                currency,
                ROW_NUMBER() OVER (PARTITION BY name ORDER BY last_updated DESC) as rn
            FROM assets
        ),
        ConvertedAssets AS (
            SELECT
                ra.name,
                ra.amount / c.rate AS amount_usd,
                ra.rn
            FROM RankedAssets ra
            JOIN currency c ON ra.currency = c.name
        )
        SELECT
            SUM(CASE WHEN rn = 1 THEN amount_usd ELSE 0 END) AS current_total,
            SUM(CASE WHEN rn = 2 THEN amount_usd ELSE 0 END) AS previous_total
        FROM ConvertedAssets;
    """)
    assets_data = cur.fetchone()

    current_asset_total = float(assets_data['current_total']) if assets_data and assets_data['current_total'] is not None else 0.0
    previous_asset_total = float(assets_data['previous_total']) if assets_data and assets_data['previous_total'] is not None else 0.0

    # Get current total of all withdrawals
    cur.execute("SELECT SUM(d.amount / c.rate) as total FROM drawings d JOIN currency c ON d.currency = c.name")
    total_withdrawals_row = cur.fetchone()
    total_withdrawals = total_withdrawals_row['total'] if total_withdrawals_row and total_withdrawals_row['total'] is not None else 0

    # Get current total of all deposits
    cur.execute("SELECT SUM(d.amount / c.rate) as total FROM deposits d JOIN currency c ON d.currency = c.name")
    total_deposits_row = cur.fetchone()
    total_deposits = total_deposits_row['total'] if total_deposits_row and total_deposits_row['total'] is not None else 0

    total_bankroll = float(current_poker_total) + float(current_asset_total)
    total_profit = float(total_bankroll) - float(total_deposits) + float(total_withdrawals)

    cur.close()
    conn.close()
    return render_template("index.html",
                           current_poker_total=current_poker_total,
                           previous_poker_total=previous_poker_total,
                           current_asset_total=current_asset_total,
                           previous_asset_total=previous_asset_total,
                           total_withdrawals=total_withdrawals,
                           total_deposits=total_deposits,
                           total_bankroll=total_bankroll,
                           total_profit=total_profit)

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email

class DummyLoginForm(FlaskForm):
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

@home_bp.route("/debug_login")
def debug_login():
    dummy_form = DummyLoginForm()
    return render_template("security/login_user.html", form=dummy_form)

