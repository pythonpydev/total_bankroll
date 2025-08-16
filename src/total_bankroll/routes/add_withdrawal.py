from flask import Blueprint, render_template, redirect, request, url_for
import psycopg2
import psycopg2.extras
from ..db import get_db
from datetime import datetime

add_withdrawal_bp = Blueprint("add_withdrawal", __name__)

@add_withdrawal_bp.route("/add_withdrawal", methods=["GET", "POST"])
def add_withdrawal():
    """Add a withdrawal transaction."""
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
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
            amount = float(amount_str)
            withdrawn_at = float(withdrawn_at_str)
            if amount <= 0:
                cur.close()
                conn.close()
                return "Amount must be positive", 400
        except ValueError:
            cur.close()
            conn.close()
            return "Invalid amount or withdrawn_at format", 400

        last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cur.execute("INSERT INTO drawings (date, amount, withdrawn_at, last_updated, currency) VALUES (%s, %s, %s, %s, %s)", (date, amount, withdrawn_at, last_updated, currency_name))
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
                SUM(CASE WHEN rn = 1 THEN amount_usd ELSE 0 END) AS current_total
            FROM ConvertedSites;
        """)
        poker_sites_data = cur.fetchone()
        current_poker_total = float(poker_sites_data['current_total']) if poker_sites_data and poker_sites_data['current_total'] is not None else 0.0

        # Get current asset totals
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
                SUM(CASE WHEN rn = 1 THEN amount_usd ELSE 0 END) AS current_total
            FROM ConvertedAssets;
        """)
        assets_data = cur.fetchone()
        current_asset_total = float(assets_data['current_total']) if assets_data and assets_data['current_total'] is not None else 0.0

        # Get current total of all withdrawals
        cur.execute("SELECT SUM(d.amount / c.rate) FROM drawings d JOIN currency c ON d.currency = c.name")
        total_withdrawals = cur.fetchone()[0]
        if total_withdrawals is None:
            total_withdrawals = 0

        # Get current total of all deposits
        cur.execute("SELECT SUM(d.amount / c.rate) FROM deposits d JOIN currency c ON d.currency = c.name")
        total_deposits = cur.fetchone()[0]
        if total_deposits is None:
            total_deposits = 0

        total_bankroll = current_poker_total + current_asset_total
        total_profit = total_bankroll - total_deposits + total_withdrawals

        cur.close()
        conn.close()
        return render_template("add_withdrawal.html", today=today, currencies=currencies, total_profit=total_profit)
