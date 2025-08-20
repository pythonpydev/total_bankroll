from flask import Blueprint, render_template, redirect, request, url_for
from flask_security import login_required, current_user
from ..db import get_db
from datetime import datetime
from decimal import Decimal

assets_bp = Blueprint("assets", __name__)

@assets_bp.route("/assets")
@login_required
def assets_page():
    """Assets page."""
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT name, rate, symbol FROM currency")
    currency_data = cur.fetchall()
    currency_rates = {row['name']: row['rate'] for row in currency_data}
    currency_symbols = {row['name']: row['symbol'] for row in currency_data}

    # Get current and previous asset totals
    cur.execute("""
        WITH RankedAssets AS (
            SELECT
                id,
                name,
                amount,
                last_updated,
                currency,
                ROW_NUMBER() OVER (PARTITION BY name ORDER BY last_updated DESC) as rn
            FROM assets
            WHERE user_id = %s
        )
        SELECT
            a1.id,
            a1.name,
            a1.amount AS current_amount,
            a2.amount AS previous_amount,
            a1.currency,
            a2.currency AS previous_currency
        FROM RankedAssets a1
        LEFT JOIN RankedAssets a2
            ON a1.name = a2.name AND a2.rn = 2
        WHERE a1.rn = 1
        ORDER BY a1.name
    """, (current_user.id,))
    assets_data_raw = cur.fetchall()

    assets_data = []
    for asset in assets_data_raw:
        converted_asset = dict(asset) # Create a mutable dictionary from the DictRow
        original_amount = converted_asset['current_amount']
        original_previous_amount = converted_asset['previous_amount']
        currency = converted_asset['currency']
        previous_currency = converted_asset['previous_currency']

        rate = currency_rates.get(currency, 1.0) # Default to 1.0 if rate not found
        previous_rate = currency_rates.get(previous_currency, 1.0)

        converted_asset['current_amount_usd'] = original_amount / rate
        converted_asset['previous_amount_usd'] = Decimal(original_previous_amount / previous_rate if original_previous_amount is not None else 0.0)

        # Add currency symbols to the asset data
        converted_asset['currency_symbol'] = currency_symbols.get(currency, currency)
        converted_asset['previous_currency_symbol'] = currency_symbols.get(previous_currency, previous_currency) if previous_currency else None

        assets_data.append(converted_asset)

    total_current = sum(asset['current_amount_usd'] for asset in assets_data)
    total_previous = sum(asset['previous_amount_usd'] if asset['previous_amount_usd'] is not None else 0 for asset in assets_data)

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
    return render_template("assets.html", assets=assets_data, currencies=currencies, total_current=total_current, total_previous=total_previous)

@assets_bp.route("/add_asset", methods=["GET", "POST"])
@login_required
def add_asset():
    """Add an asset."""
    print("add_asset function called")
    conn = get_db()
    cur = conn.cursor()
    if request.method == "POST":
        print("add_asset: POST request")
        name = request.form.get("name", "").title()
        amount_str = request.form.get("amount", "")
        currency_name = request.form.get("currency", "US Dollar") # Store currency name directly from form

        if not name or not amount_str:
            cur.close()
            conn.close()
            print("add_asset: Name or amount missing")
            return "Name and amount are required", 400

        try:
            amount = float(amount_str)
            if amount <= 0:
                cur.close()
                conn.close()
                print("add_asset: Amount not positive")
                return "Amount must be positive", 400
        except ValueError:
            cur.close()
            conn.close()
            print("add_asset: Invalid amount format")
            return "Invalid amount format", 400

        last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cur.execute("INSERT INTO assets (name, amount, last_updated, currency, user_id) VALUES (%s, %s, %s, %s, %s)", (name, amount, last_updated, currency_name, current_user.id))
        conn.commit()
        cur.close()
        conn.close()
        print("add_asset: Asset added, redirecting")
        return redirect(url_for("assets.assets_page"))
    else:
        print("add_asset: GET request")
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
        print("add_asset: Rendering add_asset.html")
        return render_template("add_asset.html", currencies=currencies)

@assets_bp.route("/update_asset/<string:asset_name>", methods=["GET", "POST"])
@login_required
def update_asset(asset_name):
    """Update an asset."""
    conn = get_db()
    cur = conn.cursor()
    if request.method == "POST":
        name = request.form.get("name", "").title()
        amount_str = request.form.get("amount", "")

        try:
            amount = round(float(amount_str), 2)
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
        cur.execute("INSERT INTO assets (name, amount, last_updated, currency, user_id) VALUES (%s, %s, %s, %s, %s)", (name, amount, last_updated, currency_name, current_user.id))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("assets.assets_page"))
    else:
        cur.execute("SELECT * FROM assets WHERE name = %s AND user_id = %s ORDER BY last_updated DESC", (asset_name, current_user.id))
        asset = cur.fetchone()
        if asset is None:
            cur.close()
            conn.close()
            return "Asset not found", 404

        cur.execute("SELECT amount FROM assets WHERE name = %s AND user_id = %s ORDER BY last_updated DESC LIMIT 1, 1", (asset_name, current_user.id))
        previous_amount_row = cur.fetchone()
        previous_amount = previous_amount_row['amount'] if previous_amount_row and 'amount' in previous_amount_row else None

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