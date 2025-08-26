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

    # Get all assets for the user
    cur.execute("SELECT id, name FROM assets WHERE user_id = %s ORDER BY name", (current_user.id,))
    assets = cur.fetchall()

    assets_data = []
    for asset in assets:
        # Get the latest two history records for each asset
        cur.execute("""
            SELECT amount, currency
            FROM asset_history
            WHERE asset_id = %s AND user_id = %s
            ORDER BY recorded_at DESC
            LIMIT 2
        """, (asset['id'], current_user.id))
        history_records = cur.fetchall()

        current_amount = 0.0
        previous_amount = 0.0
        currency = "US Dollar"
        previous_currency = "US Dollar"

        if len(history_records) > 0:
            current_amount = history_records[0]['amount']
            currency = history_records[0]['currency']
        if len(history_records) > 1:
            previous_amount = history_records[1]['amount']
            previous_currency = history_records[1]['currency']

        rate = Decimal(str(currency_rates.get(currency, 1.0)))
        previous_rate = Decimal(str(currency_rates.get(previous_currency, 1.0)))

        current_amount_usd = current_amount / rate
        previous_amount_usd = previous_amount / previous_rate

        assets_data.append({
            'id': asset['id'],
            'name': asset['name'],
            'current_amount': current_amount,
            'previous_amount': previous_amount,
            'currency': currency,
            'previous_currency': previous_currency,
            'current_amount_usd': current_amount_usd,
            'previous_amount_usd': previous_amount_usd,
            'currency_symbol': currency_symbols.get(currency, currency),
            'previous_currency_symbol': currency_symbols.get(previous_currency, previous_currency)
        })

    total_current = sum(asset['current_amount_usd'] for asset in assets_data)
    total_previous = sum(asset['previous_amount_usd'] for asset in assets_data)

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

        # Insert into assets table
        cur.execute("INSERT INTO assets (name, user_id) VALUES (%s, %s)", (name, current_user.id))
        asset_id = cur.lastrowid

        # Insert into asset_history table
        recorded_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cur.execute("INSERT INTO asset_history (asset_id, amount, currency, recorded_at, user_id) VALUES (%s, %s, %s, %s, %s)", (asset_id, amount, currency_name, recorded_at, current_user.id))

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

@assets_bp.route("/update_asset/<int:asset_id>", methods=["GET", "POST"])
@login_required
def update_asset(asset_id):
    """Update an asset."""
    conn = get_db()
    cur = conn.cursor()
    if request.method == "POST":
        amount_str = request.form.get("amount", "")
        currency_name = request.form.get("currency", "US Dollar")

        if not amount_str:
            cur.close()
            conn.close()
            return redirect(url_for("assets.assets_page"))

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

        recorded_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cur.execute("INSERT INTO asset_history (asset_id, amount, currency, recorded_at, user_id) VALUES (%s, %s, %s, %s, %s)", (asset_id, amount, currency_name, recorded_at, current_user.id))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("assets.assets_page"))
    else:
        # Get latest asset info
        cur.execute("SELECT * FROM assets WHERE id = %s AND user_id = %s", (asset_id, current_user.id))
        asset = cur.fetchone()
        if asset is None:
            cur.close()
            conn.close()
            return "Asset not found", 404

        # Get previous amount (second most recent entry)
        cur.execute("SELECT amount FROM asset_history WHERE asset_id = %s AND user_id = %s ORDER BY recorded_at DESC LIMIT 1, 1", (asset_id, current_user.id))
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

@assets_bp.route("/rename_asset/<int:asset_id>", methods=["GET", "POST"])
@login_required
def rename_asset(asset_id):
    """Rename an asset."""
    conn = get_db()
    cur = conn.cursor()
    if request.method == "POST":
        new_name = request.form.get("new_name", "").title()
        if not new_name:
            cur.close()
            conn.close()
            return "New name is required", 400

        cur.execute("UPDATE assets SET name = %s WHERE id = %s AND user_id = %s", (new_name, asset_id, current_user.id))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("assets.assets_page"))
    else:
        cur.execute("SELECT id, name FROM assets WHERE id = %s AND user_id = %s", (asset_id, current_user.id))
        asset = cur.fetchone()
        if asset is None:
            cur.close()
            conn.close()
            return "Asset not found", 404
        cur.close()
        conn.close()
        return render_template("rename_asset.html", asset=asset)