from flask import Blueprint, render_template, redirect, request, url_for
import psycopg2
import psycopg2.extras
from ..db import get_db
from datetime import datetime

update_asset_bp = Blueprint("update_asset", __name__)

@update_asset_bp.route("/update_asset/<string:asset_name>", methods=["GET", "POST"])
def update_asset(asset_name):
    """Update an asset."""
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == "POST":
        name = request.form.get("name", "").title()
        amount_str = request.form.get("amount", "")

        try:
            amount = float(amount_str)
            if amount <= 0:
                cur.close()
                conn.close()
                return redirect(url_for("assets.assets_page"))
        except ValueError:
            cur.close()
            conn.close()
            return redirect(url_for("assets.assets_page"))

        currency_input = request.form.get("currency", "US Dollar") # This can be name or code

        # Determine the currency name to store
        cur.execute("SELECT name FROM currency WHERE name = %s", (currency_input,))
        currency_row = cur.fetchone()
        if currency_row:
            currency_name = currency_row['name']
        else:
            cur.execute("SELECT name FROM currency WHERE code = %s", (currency_input,))
            currency_row = cur.fetchone()
            if currency_row:
                currency_name = currency_row['name']
            else:
                currency_name = "US Dollar" # Default to US Dollar if not found by name or code

        last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cur.execute("INSERT INTO assets (name, amount, last_updated, currency) VALUES (%s, %s, %s, %s)", (name, amount, last_updated, currency_name))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("assets.assets_page"))
    else:
        cur.execute("SELECT * FROM assets WHERE name = %s ORDER BY last_updated DESC", (asset_name,))
        asset = cur.fetchone()
        if asset is None:
            cur.close()
            conn.close()
            return "Asset not found", 404

        cur.execute("SELECT amount FROM assets WHERE name = %s ORDER BY last_updated DESC OFFSET 1 LIMIT 1", (asset_name,))
        previous_amount_row = cur.fetchone()
        previous_amount = previous_amount_row[0] if previous_amount_row else None

        cur.execute("""
            SELECT name, code FROM currency
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
        return render_template("update_asset.html", asset=asset, currencies=currencies, previous_amount=previous_amount)

