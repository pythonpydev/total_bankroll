from flask import Blueprint, render_template, redirect, request, url_for
import psycopg2
import psycopg2.extras
from db import get_db
from datetime import datetime

add_deposit_bp = Blueprint("add_deposit", __name__)

@add_deposit_bp.route("/add_deposit", methods=["GET", "POST"])
def add_deposit():
    """Add a deposit transaction."""
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
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
            amount = float(amount_str)
            deposited_at = float(deposited_at_str)
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
        cur.execute("INSERT INTO deposits (date, amount, deposited_at, last_updated, currency) VALUES (%s, %s, %s, %s, %s)", (date, amount, deposited_at, last_updated, currency_name))
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
        # Recalculate total_net_worth for the form
        cur.execute("""
            SELECT
                SUM(amount) AS current_total
            FROM sites
            WHERE last_updated = (SELECT MAX(last_updated) FROM sites)
        """)
        poker_sites_data = cur.fetchone()
        current_poker_total = poker_sites_data['current_total'] if poker_sites_data and poker_sites_data['current_total'] is not None else 0

        cur.execute("""
            SELECT
                SUM(amount) AS current_total
            FROM assets
            WHERE last_updated = (SELECT MAX(last_updated) FROM assets)
        """)
        assets_data = cur.fetchone()
        current_asset_total = assets_data['current_total'] if assets_data and assets_data['current_total'] is not None else 0

        cur.execute("SELECT SUM(amount) FROM drawings")
        total_withdrawals = cur.fetchone()[0]
        if total_withdrawals is None:
            total_withdrawals = 0

        total_net_worth = current_poker_total + current_asset_total - total_withdrawals

        cur.close()
        conn.close()
        return render_template("add_deposit.html", today=today, currencies=currencies, total_net_worth=total_net_worth)
