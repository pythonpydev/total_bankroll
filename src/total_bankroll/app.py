"""Web entry point for total_bankroll."""

from flask import Flask, Blueprint, render_template, request, redirect, url_for
import psycopg2
import psycopg2.extras
from datetime import datetime
# import os # No longer needed for PostgreSQL

import currency 
from db import get_db, close_db
from routes.home import home_bp
from routes.poker_sites import poker_sites_bp 
from routes.assets import assets_bp
from routes.add_asset import add_asset_bp
from routes.update_asset import update_asset_bp
from routes.add_poker_site import add_site_bp
from routes.update_poker_site import update_site_bp

app = Flask(__name__)

# Close db after each request
app.teardown_appcontext(close_db)

# Register blueprints
app.register_blueprint(home_bp)
app.register_blueprint(poker_sites_bp)
app.register_blueprint(assets_bp)
app.register_blueprint(add_asset_bp)
app.register_blueprint(update_asset_bp)
app.register_blueprint(add_site_bp)
app.register_blueprint(update_site_bp)

@app.route("/withdrawal")
def withdrawal():
    """Withdrawal page."""
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

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
    cur.execute("SELECT SUM(amount) FROM drawings")
    total_withdrawals = cur.fetchone()[0]
    if total_withdrawals is None:
        total_withdrawals = 0

    total_net_worth = current_poker_total + current_asset_total - total_withdrawals

    cur.execute("SELECT id, date, CAST(amount AS REAL) as amount, CAST(withdrawn_at AS REAL) as withdrawn_at, last_updated, currency FROM drawings")
    withdrawal_data = cur.fetchall()
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
    return render_template("withdrawal.html", drawings=withdrawal_data, today=today, total_net_worth=total_net_worth, currencies=currencies)


@app.route("/add_withdrawal", methods=["GET", "POST"])
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
        return redirect(url_for("withdrawal"))
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
        return render_template("add_withdrawal.html", today=today, currencies=currencies, total_net_worth=total_net_worth)


@app.route("/deposit")
def deposit():
    """Deposit page."""
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

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
    cur.execute("SELECT SUM(amount) FROM drawings")
    total_withdrawals = cur.fetchone()[0]
    if total_withdrawals is None:
        total_withdrawals = 0

    total_net_worth = current_poker_total + current_asset_total - total_withdrawals

    cur.execute("SELECT id, date, CAST(amount AS REAL) as amount, CAST(deposited_at AS REAL) as deposited_at, last_updated, currency FROM deposits")
    deposit_data = cur.fetchall()
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


@app.route("/add_deposit", methods=["GET", "POST"])
def add_deposit():
    """Add a deposit transaction."""
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == "POST":
        date = request.form.get("date", "")
        amount_str = request.form.get("amount", "")
        deposited_at_str = request.form.get("deposited_at", "")
        currency_name = request.form.get("currency", "USD")

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

        last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cur.execute("INSERT INTO deposits (date, amount, deposited_at, last_updated, currency) VALUES (%s, %s, %s, %s, %s)", (date, amount, deposited_at, last_updated, currency_name))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("deposit"))
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


@app.route("/update_deposit/<int:deposit_id>", methods=["GET", "POST"])
def update_deposit(deposit_id):
    """Update a deposit record."""
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == "POST":
        date = request.form["date"]
        amount_str = request.form["amount"]
        deposited_at_str = request.form["deposited_at"]
        currency_name = request.form["currency"]

        if not date or not amount_str or not deposited_at_str:
            cur.close()
            conn.close()
            return redirect(url_for("deposit"))

        try:
            amount = float(amount_str)
            deposited_at = float(deposited_at_str)
            if amount <= 0 or deposited_at < 0:
                cur.close()
                conn.close()
                return redirect(url_for("deposit"))
        except ValueError:
            cur.close()
            conn.close()
            return redirect(url_for("deposit"))

        # Get the exchange rate for the selected currency
        cur.execute("SELECT rate FROM currency WHERE name = %s", (currency_name,))
        currency_rate_row = cur.fetchone()
        if currency_rate_row:
            exchange_rate = currency_rate_row['rate']
            amount_usd = amount / exchange_rate  # Convert to USD
        else:
            amount_usd = amount # Default to no conversion if currency not found

        last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cur.execute("INSERT INTO deposits (date, amount, deposited_at, last_updated, currency) VALUES (%s, %s, %s, %s, %s)", (date, amount_usd, deposited_at, last_updated, currency_name))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("deposit"))
    else:
        cur.execute("SELECT * FROM deposits WHERE id = %s", (deposit_id,))
        deposit_item = cur.fetchone()
        if deposit_item is None:
            cur.close()
            conn.close()
            return "Deposit record not found", 404
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
        return render_template("update_deposit.html", deposit_item=deposit_item, currencies=currencies)


@app.route("/update_withdrawal/<int:withdrawal_id>", methods=["GET", "POST"])
def update_withdrawal(withdrawal_id):
    """Update a withdrawal record."""
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == "POST":
        date = request.form["date"]
        amount_str = request.form["amount"]
        withdrawn_at_str = request.form["withdrawn_at"]
        currency_name = request.form["currency"]

        if not date or not amount_str or not withdrawn_at_str:
            cur.close()
            conn.close()
            return redirect(url_for("withdrawal"))

        try:
            amount = float(amount_str)
            withdrawn_at = float(withdrawn_at_str)
            if amount <= 0:
                cur.close()
                conn.close()
                return redirect(url_for("withdrawal"))
        except ValueError:
            cur.close()
            conn.close()
            return redirect(url_for("withdrawal"))

        # Get the exchange rate for the selected currency
        cur.execute("SELECT rate FROM currency WHERE name = %s", (currency_name,))
        currency_rate_row = cur.fetchone()
        if currency_rate_row:
            exchange_rate = currency_rate_row['rate']
            amount_usd = amount / exchange_rate  # Convert to USD
        else:
            amount_usd = amount # Default to no conversion if currency not found

        last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cur.execute("INSERT INTO drawings (date, amount, withdrawn_at, last_updated, currency) VALUES (%s, %s, %s, %s, %s)", (date, amount_usd, withdrawn_at, last_updated, currency_name))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("withdrawal"))
    else:
        cur.execute("SELECT * FROM drawings WHERE id = %s", (withdrawal_id,))
        withdrawal_item = cur.fetchone()
        if withdrawal_item is None:
            cur.close()
            conn.close()
            return "Withdrawal record not found", 404
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
        return render_template("update_withdrawal.html", withdrawal_item=withdrawal_item, currencies=currencies)


@app.route("/update_exchange_rates", methods=["POST"])
def update_exchange_rates():
    """Triggers an update of exchange rates (handled by the agent)."""
    # This function will be handled by the agent to update rates.
    # For now, it just redirects.
    return redirect(url_for("currencies"))


@app.route("/confirm_delete/<string:item_type>/<int:item_id>")
def confirm_delete(item_type, item_id):
    """Render confirmation dialog for deletion."""
    return render_template("confirm_delete.html", item_type=item_type, item_id=item_id)


@app.route("/currencies")
def currencies():
    """Currencies page."""
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("""
        SELECT id, name, rate, code, symbol FROM currency
        ORDER BY
            CASE name
                WHEN 'US Dollar' THEN 1
                WHEN 'British Pound' THEN 2
                WHEN 'Euro' THEN 3
                ELSE 4
            END,
            name
    """)
    currencies_data = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("currencies.html", currencies=currencies_data)


@app.route("/perform_delete/<string:item_type>/<int:item_id>")
def perform_delete(item_type, item_id):
    """Perform the actual deletion based on item_type and item_id."""
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    if item_type == "site":
        # First, get the site name for the given ID
        cur.execute("SELECT name FROM sites WHERE id = %s", (item_id,))
        site_record = cur.fetchone()
        if site_record:
            site_name = site_record['name']
            # Delete all sites with the same name
            cur.execute("DELETE FROM sites WHERE name = %s", (site_name,))
            conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("poker_sites.poker_sites_page"))
        
    elif item_type == "asset":
        # First, get the asset name for the given ID
        cur.execute("SELECT name FROM assets WHERE id = %s", (item_id,))
        asset_record = cur.fetchone()
        if asset_record:
            asset_name = asset_record['name']
            # Delete all assets with the same name
            cur.execute("DELETE FROM assets WHERE name = %s", (asset_name,))
            conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("assets.assets_page"))
        
    elif item_type == "withdrawal":
        cur.execute("DELETE FROM drawings WHERE id = %s", (item_id,))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("withdrawal"))
        
    elif item_type == "deposit":
        cur.execute("DELETE FROM deposits WHERE id = %s", (item_id,))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("deposit"))
        
    else:
        cur.close()
        conn.close()
        return "Invalid item type", 400


@app.route("/settings")
def settings_page():
    """Settings page."""
    return render_template("settings.html")


@app.route("/about")
def about_page():
    """About page."""
    return render_template("about.html")


if __name__ == "__main__":
    currency.insert_initial_currency_data(app)
    app.run(debug=True)