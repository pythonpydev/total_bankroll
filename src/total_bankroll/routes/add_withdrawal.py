from flask import Blueprint, render_template, redirect, request, url_for
from flask_security import login_required, current_user
import pymysql
from ..db import get_db
from datetime import datetime

add_withdrawal_bp = Blueprint("add_withdrawal", __name__)

@add_withdrawal_bp.route("/add_withdrawal", methods=["GET", "POST"])
@login_required
def add_withdrawal():
    """Add a withdrawal transaction."""
    conn = get_db()
    cur = conn.cursor()
    if request.method == "POST":
        date = request.form.get("date", "")
        amount_str = request.form.get("amount", "")
        withdrawn_at_str = request.form.get("withdrawn_at", "")
        currency_name = request.form.get("currency", "USD")

        if not date or not amount_str or not withdrawn_at_str:
            cur.close()
            conn.close()
            return "Date, amount, and withdrawn_at are required", 400

        try:
            amount = round(float(amount_str), 2)
            withdrawn_at = round(float(withdrawn_at_str), 2)
            if amount <= 0:
                cur.close()
                conn.close()
                return "Amount must be positive", 400
        except ValueError:
            cur.close()
            conn.close()
            return "Invalid amount or withdrawn_at format", 400

        last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cur.execute("INSERT INTO drawings (date, amount, withdrawn_at, last_updated, currency, user_id) VALUES (%s, %s, %s, %s, %s, %s)", (date, amount, withdrawn_at, last_updated, currency_name, current_user.id))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("withdrawal.withdrawal"))
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

        # Get current total of all withdrawals
        cur.execute("SELECT SUM(d.amount / c.rate) as total FROM drawings d JOIN currency c ON d.currency = c.name WHERE d.user_id = %s", (current_user.id,))
        total_withdrawals_row = cur.fetchone()
        total_withdrawals = total_withdrawals_row['total'] if total_withdrawals_row and total_withdrawals_row['total'] is not None else 0

        # Get current total of all deposits
        cur.execute("SELECT SUM(d.amount / c.rate) as total FROM deposits d JOIN currency c ON d.currency = c.name WHERE d.user_id = %s", (current_user.id,))
        total_deposits_row = cur.fetchone()
        total_deposits = total_deposits_row['total'] if total_deposits_row and total_deposits_row['total'] is not None else 0

        total_bankroll = current_poker_total + current_asset_total
        total_profit = total_bankroll - total_deposits + total_withdrawals

        cur.close()
        conn.close()
        return render_template("add_withdrawal.html", today=today, currencies=currencies, total_profit=total_profit, total_bankroll=total_bankroll)