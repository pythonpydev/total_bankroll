from flask import Blueprint, render_template, redirect, request, url_for
from flask_security import login_required, current_user
import pymysql
from ..db import get_db
from datetime import datetime

withdrawal_bp = Blueprint("withdrawal", __name__)

@withdrawal_bp.route("/withdrawal")
@login_required
def withdrawal():
    """Withdrawal page."""
    conn = get_db()
    cur = conn.cursor()

    # Get currency symbols
    cur.execute("SELECT name, symbol FROM currency")
    currency_symbols = {row['name']: row['symbol'] for row in cur.fetchall()}

    # Get current poker site totals
    cur.execute("""
        SELECT
            SUM(amount) AS current_total
        FROM sites
        WHERE last_updated = (SELECT MAX(last_updated) FROM sites WHERE user_id = %s) AND user_id = %s
    """, (current_user.id, current_user.id))
    poker_sites_data = cur.fetchone()
    current_poker_total = poker_sites_data['current_total'] if poker_sites_data and poker_sites_data['current_total'] is not None else 0

    # Get current asset totals
    cur.execute("""
        SELECT
            SUM(amount) AS current_total
        FROM assets
        WHERE last_updated = (SELECT MAX(last_updated) FROM assets WHERE user_id = %s) AND user_id = %s
    """, (current_user.id, current_user.id))
    assets_data = cur.fetchone()
    current_asset_total = assets_data['current_total'] if assets_data and assets_data['current_total'] is not None else 0

    # Get current total of all withdrawals
    cur.execute("SELECT SUM(amount) as total FROM drawings WHERE user_id = %s", (current_user.id,))
    total_withdrawals_row = cur.fetchone()
    total_withdrawals = total_withdrawals_row['total'] if total_withdrawals_row and total_withdrawals_row['total'] is not None else 0

    total_net_worth = current_poker_total + current_asset_total - total_withdrawals

    # Get deposits with currency conversion to USD
    cur.execute("""
        SELECT
            d.id,
            d.date,
            CAST(d.amount AS REAL) as original_amount,
            CAST(d.withdrawn_at AS REAL) as original_withdrawn_at,
            d.last_updated,
            COALESCE(d.currency, 'US Dollar') as currency,
            COALESCE(c.rate, 1.0) as exchange_rate
        FROM drawings d
        LEFT JOIN currency c ON d.currency = c.name
        WHERE d.user_id = %s
        ORDER BY d.date DESC
    """, (current_user.id,))
    withdrawals_raw = cur.fetchall()

    # Process withdrawals to add USD calculations and currency symbols
    withdrawal_data = []
    for withdrawal in withdrawals_raw:
        withdrawal_dict = dict(withdrawal)
        withdrawal_dict['amount_usd'] = float(withdrawal['original_amount']) / float(withdrawal['exchange_rate'])
        withdrawal_dict['withdrawn_at_usd'] = float(withdrawal['original_withdrawn_at']) / float(withdrawal['exchange_rate'])
        withdrawal_dict['currency_symbol'] = currency_symbols.get(withdrawal['currency'], withdrawal['currency'])
        withdrawal_data.append(withdrawal_dict)

    today = datetime.now().strftime("%Y-%m-%d")
    cur.execute("""
        SELECT name FROM currency
        ORDER BY
            CASE name
                WHEN 'US Dollar' THEN 1
                WHEN 'British Pound' THEN 2
                WHEN 'Euro' THEN 3
                ELSE 4
            END,
            name
    """)
    currencies = cur.fetchall()

    cur.close()
    conn.close()
    return render_template("withdrawal.html", drawings=withdrawal_data, today=today, total_net_worth=total_net_worth, currencies=currencies)