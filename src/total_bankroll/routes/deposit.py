from flask import Blueprint, render_template, redirect, request, url_for
import psycopg2
import psycopg2.extras
from ..db import get_db
from datetime import datetime

deposit_bp = Blueprint("deposit", __name__)

@deposit_bp.route("/deposit")
def deposit():
    """Deposit page."""
    conn = get_db()
    cur = conn.cursor(dictionary=True)

    try:
        # Get currency symbols
        cur.execute("SELECT name, symbol FROM currency")
        currency_symbols = {row['name']: row['symbol'] for row in cur.fetchall()}

        # Get current poker site totals
        cur.execute("""
            SELECT
                SUM(amount) AS current_total
            FROM sites
            WHERE last_updated = (SELECT MAX(last_updated) FROM sites)
        """)
        poker_sites_data = cur.fetchone()
        current_poker_total = poker_sites_data['current_total'] if poker_sites_data and poker_sites_data['current_total'] is not None else 0

        # Get current asset totals
        cur.execute("""
            SELECT
                SUM(amount) AS current_total
            FROM assets
            WHERE last_updated = (SELECT MAX(last_updated) FROM assets)
        """)
        assets_data = cur.fetchone()
        current_asset_total = assets_data['current_total'] if assets_data and assets_data['current_total'] is not None else 0

        # Get current total of all withdrawals
        cur.execute("SELECT SUM(amount) as total FROM drawings")
        total_withdrawals_row = cur.fetchone()
        total_withdrawals = total_withdrawals_row['total'] if total_withdrawals_row and total_withdrawals_row['total'] is not None else 0

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
            ORDER BY d.date DESC
        """)
        deposits_raw = cur.fetchall()
        
        # Process deposits to add USD calculations and currency symbols
        deposit_data = []
        for deposit in deposits_raw:
            deposit_dict = dict(deposit)
            deposit_dict['amount_usd'] = float(deposit['original_amount']) / float(deposit['exchange_rate'])
            deposit_dict['deposited_at_usd'] = float(deposit['original_deposited_at']) / float(deposit['exchange_rate'])
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
        conn.close()
        return render_template("deposit.html", deposits=deposit_data, today=today, total_net_worth=total_net_worth, currencies=currencies)
        
    except Exception as e:
        cur.close()
        conn.close()
        import traceback
        traceback.print_exc()
        return f"Error loading deposits: {str(e)}", 500
