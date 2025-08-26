from flask import Blueprint, render_template, redirect, request, url_for
from flask_security import login_required, current_user
import pymysql
from ..db import get_db
from datetime import datetime

add_deposit_bp = Blueprint("add_deposit", __name__)

@add_deposit_bp.route("/add_deposit", methods=["GET", "POST"])
@login_required
def add_deposit():
    """Add a deposit transaction."""
    conn = get_db()
    cur = conn.cursor()
    if request.method == "POST":
        date = request.form.get("date", "")
        amount_str = request.form.get("amount", "")
        deposited_at_str = request.form.get("deposited_at", "")
        currency_name = request.form.get("currency", "US Dollar")

        if not date or not amount_str or not deposited_at_str:
            cur.close()
            conn.close()
            return "Date, amount, and deposited_at are required", 400

        try:
            amount = round(float(amount_str), 2)
            deposited_at = round(float(deposited_at_str), 2)
            if amount <= 0 or deposited_at < 0:
                cur.close()
                conn.close()
                return "Amount must be positive and deposited_at non-negative", 400
        except ValueError:
            cur.close()
            conn.close()
            return "Invalid amount or deposited_at format", 400

        # Store the amount in original currency - conversion will happen on display
        last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cur.execute("INSERT INTO deposits (date, amount, deposited_at, last_updated, currency, user_id) VALUES (%s, %s, %s, %s, %s, %s)", (date, amount, deposited_at, last_updated, currency_name, current_user.id))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("deposit.deposit"))
    else:
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

        # Get current poker site totals
        cur.execute("""
            SELECT
                SUM(sh.amount / c.rate) AS current_total
            FROM site_history sh
            JOIN sites s ON sh.site_id = s.id
            JOIN currency c ON sh.currency = c.name
            WHERE sh.user_id = %s
            AND sh.recorded_at = (SELECT MAX(recorded_at) FROM site_history WHERE site_id = sh.site_id AND user_id = %s)
        """, (current_user.id, current_user.id))
        poker_sites_data = cur.fetchone()
        current_poker_total = poker_sites_data['current_total'] if poker_sites_data and poker_sites_data['current_total'] is not None else Decimal(0)

        # Get current asset totals
        cur.execute("""
            SELECT
                SUM(ah.amount / c.rate) AS current_total
            FROM asset_history ah
            JOIN assets a ON ah.asset_id = a.id
            JOIN currency c ON ah.currency = c.name
            WHERE ah.user_id = %s
            AND ah.recorded_at = (SELECT MAX(recorded_at) FROM asset_history WHERE asset_id = ah.asset_id AND user_id = %s)
        """, (current_user.id, current_user.id))
        assets_data = cur.fetchone()
        current_asset_total = assets_data['current_total'] if assets_data and assets_data['current_total'] is not None else Decimal(0)

        # Get current total of all withdrawals - FIXED: Use dictionary key instead of index
        cur.execute("SELECT SUM(d.amount / c.rate) as total_withdrawals FROM drawings d JOIN currency c ON d.currency = c.name WHERE d.user_id = %s", (current_user.id,))
        withdrawal_result = cur.fetchone()
        total_withdrawals = withdrawal_result['total_withdrawals'] if withdrawal_result and withdrawal_result['total_withdrawals'] is not None else 0

        # Get current total of all deposits
        cur.execute("SELECT SUM(d.amount / c.rate) as total FROM deposits d JOIN currency c ON d.currency = c.name WHERE d.user_id = %s", (current_user.id,))
        total_deposits_row = cur.fetchone()
        total_deposits = total_deposits_row['total'] if total_deposits_row and total_deposits_row['total'] is not None else 0

        total_bankroll = current_poker_total + current_asset_total
        total_profit = total_bankroll - total_deposits + total_withdrawals

        cur.close()
        conn.close()
        return render_template("add_deposit.html", today=today, currencies=currencies, total_profit=total_profit)
