from flask import Blueprint, render_template, redirect, request, url_for
from flask_security import login_required, current_user
import pymysql
from ..db import get_db
from datetime import datetime
from decimal import Decimal

deposit_bp = Blueprint("deposit", __name__)

@deposit_bp.route("/deposit")
@login_required
def deposit():
    """Deposit page."""
    conn = get_db()
    cur = conn.cursor()

    try:
        # Get currency symbols
        cur.execute("SELECT name, symbol FROM currency")
        currency_symbols = {row['name']: row['symbol'] for row in cur.fetchall()}

        # Get current poker site totals from site_history
        cur.execute("""
            SELECT SUM(sh.amount) AS current_total
            FROM sites s
            JOIN site_history sh ON s.id = sh.site_id
            WHERE sh.recorded_at = (
                SELECT MAX(recorded_at)
                FROM site_history
                WHERE site_id = s.id AND user_id = %s
            ) AND s.user_id = %s
        """, (current_user.id, current_user.id))
        poker_sites_data = cur.fetchone()
        current_poker_total = Decimal(str(poker_sites_data['current_total'])) if poker_sites_data and poker_sites_data['current_total'] is not None else Decimal('0')

        # Get current asset totals from asset_history
        cur.execute("""
            SELECT SUM(ah.amount) AS current_total
            FROM assets a
            JOIN asset_history ah ON a.id = ah.asset_id
            WHERE ah.recorded_at = (
                SELECT MAX(recorded_at)
                FROM asset_history
                WHERE asset_id = a.id AND user_id = %s
            ) AND a.user_id = %s
        """, (current_user.id, current_user.id))
        assets_data = cur.fetchone()
        current_asset_total = Decimal(str(assets_data['current_total'])) if assets_data and assets_data['current_total'] is not None else Decimal('0')

        # Get current total of all withdrawals
        cur.execute("SELECT SUM(amount) as total FROM drawings WHERE user_id = %s", (current_user.id,))
        total_withdrawals_row = cur.fetchone()
        total_withdrawals = Decimal(str(total_withdrawals_row['total'])) if total_withdrawals_row and total_withdrawals_row['total'] is not None else Decimal('0')

        total_net_worth = current_poker_total + current_asset_total - total_withdrawals

        # Get deposits with currency conversion to USD
        cur.execute("""
            SELECT
                d.id,
                d.date,
                CAST(d.amount AS REAL) as original_amount,
                CAST(d.deposited_at AS REAL) as original_deposited_at,
                d.last_updated,
                COALESCE(d.currency, 'US Dollar') as currency,
                COALESCE(c.rate, 1.0) as exchange_rate
            FROM deposits d
            LEFT JOIN currency c ON d.currency = c.name
            WHERE d.user_id = %s
            ORDER BY d.date DESC
        """, (current_user.id,))
        deposits_raw = cur.fetchall()

        # Process deposits to add USD calculations and currency symbols
        deposit_data = []
        for deposit in deposits_raw:
            deposit_dict = dict(deposit)
            deposit_dict['amount_usd'] = Decimal(str(deposit['original_amount'])) / Decimal(str(deposit['exchange_rate']))
            deposit_dict['deposited_at_usd'] = Decimal(str(deposit['original_deposited_at'])) / Decimal(str(deposit['exchange_rate']))
            deposit_dict['currency_symbol'] = currency_symbols.get(deposit['currency'], deposit['currency'])
            deposit_data.append(deposit_dict)

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
        return render_template("deposit.html", deposits=deposit_data, today=today, total_net_worth=total_net_worth, currencies=currencies)

    except Exception as e:
        cur.close()
        import traceback
        traceback.print_exc()
        return f"Error loading deposits: {str(e)}", 500