from flask import Blueprint, render_template, redirect, request, url_for
import psycopg2
import psycopg2.extras
from db import get_db
from datetime import datetime

add_asset_bp = Blueprint("add_asset", __name__)

@add_asset_bp.route("/add_asset", methods=["GET", "POST"])
def add_asset():
    """Add an asset."""
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == "POST":
        name = request.form.get("name", "").title()
        amount_str = request.form.get("amount", "")
        currency_name = request.form.get("currency", "USD")

        if not name or not amount_str:
            cur.close()
            conn.close()
            return "Name and amount are required", 400

        try:
            amount = float(amount_str)
            if amount <= 0:
                cur.close()
                conn.close()
                return "Amount must be positive", 400
        except ValueError:
            cur.close()
            conn.close()
            return "Invalid amount format", 400

        # Get the exchange rate for the selected currency
        cur.execute("SELECT rate FROM currency WHERE name = %s", (currency_name,))
        currency_rate_row = cur.fetchone()
        if currency_rate_row:
            exchange_rate = currency_rate_row['rate']
            amount_usd = amount / exchange_rate  # Convert to USD
        else:
            amount_usd = amount # Default to no conversion if currency not found

        last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cur.execute("INSERT INTO assets (name, amount, last_updated, currency) VALUES (%s, %s, %s, %s)", (name, amount_usd, last_updated, currency_name))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("assets.assets_page"))
    else:
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
        return render_template("add_asset.html", currencies=currencies)
