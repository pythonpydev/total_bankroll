from flask import Blueprint, render_template, redirect, url_for
import pymysql
from flask_security import current_user
import sys

from ..db import get_db
from decimal import Decimal

home_bp = Blueprint("home", __name__)

@home_bp.route("/")
def home():
    """Main page."""
    if not current_user.is_authenticated:
        return redirect(url_for('about.about'))

    conn = get_db()
    cur = conn.cursor()

    current_poker_total = Decimal('0')
    previous_poker_total = Decimal('0')
    current_asset_total = Decimal('0')
    previous_asset_total = Decimal('0')
    total_withdrawals = Decimal('0')
    total_deposits = Decimal('0')

    # Get current and previous poker site totals
    cur.execute("""
        SELECT
            s.id,
            s.name,
            sh.amount,
            sh.currency,
            sh.recorded_at
        FROM sites s
        JOIN site_history sh ON s.id = sh.site_id
        WHERE s.user_id = %s
        ORDER BY sh.recorded_at DESC
    """, (current_user.id,))
    poker_sites_raw_data = cur.fetchall()

    poker_sites_data = {}
    for row in poker_sites_raw_data:
        site_id = row['id']
        if site_id not in poker_sites_data:
            poker_sites_data[site_id] = {
                'name': row['name'],
                'current_amount': Decimal(str(row['amount'])),
                'current_currency': row['currency'],
                'previous_amount': Decimal('0'),
                'previous_currency': "US Dollar"
            }
        elif poker_sites_data[site_id]['previous_amount'] == Decimal('0'):
            poker_sites_data[site_id]['previous_amount'] = Decimal(str(row['amount']))
            poker_sites_data[site_id]['previous_currency'] = row['currency']

    # Get currency rates
    cur.execute("SELECT name, rate FROM currency")
    currency_rates = {row['name']: Decimal(str(row['rate'])) for row in cur.fetchall()}

    for site_id, data in poker_sites_data.items():
        current_rate = currency_rates.get(data['current_currency'], Decimal('1.0'))
        previous_rate = currency_rates.get(data['previous_currency'], Decimal('1.0'))
        current_poker_total += data['current_amount'] / current_rate
        previous_poker_total += data['previous_amount'] / previous_rate

    # Get current and previous asset totals
    cur.execute("""
        SELECT
            a.id,
            a.name,
            ah.amount,
            ah.currency,
            ah.recorded_at
        FROM assets a
        JOIN asset_history ah ON a.id = ah.asset_id
        WHERE a.user_id = %s
        ORDER BY ah.recorded_at DESC
    """, (current_user.id,))
    assets_raw_data = cur.fetchall()

    assets_data = {}
    for row in assets_raw_data:
        asset_id = row['id']
        if asset_id not in assets_data:
            assets_data[asset_id] = {
                'current_amount': Decimal(str(row['amount'])),
                'current_currency': row['currency'],
                'previous_amount': Decimal('0'),
                'previous_currency': "US Dollar"
            }
        elif assets_data[asset_id]['previous_amount'] == Decimal('0'):
            assets_data[asset_id]['previous_amount'] = Decimal(str(row['amount']))
            assets_data[asset_id]['previous_currency'] = row['currency']

    for asset_id, data in assets_data.items():
        current_rate = currency_rates.get(data['current_currency'], Decimal('1.0'))
        previous_rate = currency_rates.get(data['previous_currency'], Decimal('1.0'))
        current_asset_total += data['current_amount'] / current_rate
        previous_asset_total += data['previous_amount'] / previous_rate

    # Get current total of all withdrawals
    cur.execute("SELECT SUM(d.amount / c.rate) as total FROM drawings d JOIN currency c ON d.currency = c.name WHERE d.user_id = %s", (current_user.id,))
    total_withdrawals_row = cur.fetchone()
    total_withdrawals = Decimal(str(total_withdrawals_row['total'])) if total_withdrawals_row and total_withdrawals_row['total'] is not None else Decimal('0')

    # Get current total of all deposits
    cur.execute("SELECT SUM(d.amount / c.rate) as total FROM deposits d JOIN currency c ON d.currency = c.name WHERE d.user_id = %s", (current_user.id,))
    total_deposits_row = cur.fetchone()
    total_deposits = Decimal(str(total_deposits_row['total'])) if total_deposits_row and total_deposits_row['total'] is not None else Decimal('0')

    total_bankroll = current_poker_total + current_asset_total
    total_profit = total_bankroll - total_deposits + total_withdrawals

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