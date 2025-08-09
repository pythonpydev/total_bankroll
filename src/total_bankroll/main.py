"""Web entry point for total_bankroll."""

import psycopg2
import psycopg2.extras # Import for DictCursor
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
# import os # No longer needed for PostgreSQL

app = Flask(__name__)

# PostgreSQL connection details
DB_HOST = "localhost"
DB_NAME = "bankroll"
DB_USER = "efb"
DB_PASS = "post123!"


def get_db():
    """Get a database connection."""
    conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)
    # Use DictCursor to fetch rows as dictionaries
    return conn


def init_db():
    """Initialize the database."""
    with app.app_context():
        conn = get_db()
        cur = conn.cursor()
        print(f"Initializing database: {DB_NAME} on {DB_HOST}")
        with app.open_resource("schema_postgres.sql", mode="r") as f:
            # Read the schema and execute each statement
            # PostgreSQL doesn't support multiple statements in a single execute() call by default
            # We need to split them and execute one by one
            sql_statements = f.read().split(';')
            for statement in sql_statements:
                if statement.strip():
                    cur.execute(statement)
        conn.commit()
        cur.close()
        conn.close()
        print("Database initialization complete.")


def insert_initial_currency_data():
    """Insert initial currency data if the table is empty."""
    with app.app_context():
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM currency")
        if cur.fetchone()[0] == 0:
            currencies = [
                ('US Dollar', 1.0, 'USD', '$'),
                ('British Pound', 0.4874, 'GBP', '£'),
                ('Euro', 0.5582, 'EUR', '€'),
                ('Chinese Yuan', 4.6786, 'CNY', '¥'),
                ('Japanese Yen', 95.98, 'JPY', '¥'),
                ('Canadian Dollar', 1.4201, 'CAD', 'C$'),
                ('Australian Dollar', 0.9411, 'AUD', 'A$'),
                ('Swiss Franc', 1.7717, 'CHF', 'CHF'),
                ('New Zealand Dollar', 0.8653, 'NZD', 'NZ$'),
                ('Swedish Krona', 0.1501, 'SEK', 'kr'),
                ('Norwegian Krone', 0.1407, 'NOK', 'kr'),
                ('Danish Krone', 0.2239, 'DKK', 'kr'),
            ]
            cur.executemany("INSERT INTO currency (name, rate, code, symbol) VALUES (%s, %s, %s, %s)", currencies)
            conn.commit()
        cur.close()
        conn.close()


@app.route("/")
def index():
    """Main page."""
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Get current and previous poker site totals
    cur.execute("""
        WITH RankedSites AS (
            SELECT
                name,
                amount,
                last_updated,
                currency,
                ROW_NUMBER() OVER (PARTITION BY name ORDER BY last_updated DESC) as rn
            FROM sites
        )
        SELECT
            SUM(CASE WHEN rs.rn = 1 THEN rs.amount / c.rate ELSE 0 END) AS current_total,
            SUM(CASE WHEN rs.rn = 2 THEN rs.amount / c.rate ELSE 0 END) AS previous_total
        FROM RankedSites rs
        JOIN currency c ON rs.currency = c.name;
    """)
    poker_sites_data = cur.fetchone()

    current_poker_total = float(poker_sites_data['current_total']) if poker_sites_data and poker_sites_data['current_total'] is not None else 0.0
    previous_poker_total = float(poker_sites_data['previous_total']) if poker_sites_data and poker_sites_data['previous_total'] is not None else 0.0

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
        )
        SELECT
            a1.id,
            a1.name,
            CAST(a1.amount AS REAL) AS current_amount,
            CAST(a2.amount AS REAL) AS previous_amount,
            a1.currency
        FROM RankedAssets a1
        LEFT JOIN RankedAssets a2
            ON a1.name = a2.name AND a2.rn = 2
        WHERE a1.rn = 1
        ORDER BY a1.name
    """)
    assets_data = cur.fetchall()

    current_asset_total = sum([asset['current_amount'] for asset in assets_data])
    previous_asset_total = sum([asset['previous_amount'] if asset['previous_amount'] is not None else 0.0 for asset in assets_data])

    # Get current total of all withdrawals
    cur.execute("SELECT SUM(amount) FROM drawings")
    total_withdrawals = cur.fetchone()[0]
    if total_withdrawals is None:
        total_withdrawals = 0

    # Get current total of all deposits
    cur.execute("SELECT SUM(amount) FROM deposits")
    total_deposits = cur.fetchone()[0]
    if total_deposits is None:
        total_deposits = 0

    total_bankroll = current_poker_total + current_asset_total
    total_profit = total_bankroll - total_deposits + total_withdrawals

    cur.close()
    conn.close()
    return render_template("index.html",
                           current_poker_total=current_poker_total,
                           previous_poker_total=previous_poker_total,
                           current_asset_total=current_asset_total,
                           previous_asset_total=previous_asset_total,
                           total_withdrawals=total_withdrawals,
                           total_deposits=total_deposits,
                           total_bankroll=total_bankroll,
                           total_profit=total_profit)


@app.route("/poker_sites")
def poker_sites_page():
    """Poker Sites page."""
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("""
        WITH RankedSites AS (
            SELECT
                id,
                name,
                amount,
                last_updated,
                ROW_NUMBER() OVER (PARTITION BY name ORDER BY last_updated DESC) as rn
            FROM sites
        )
        SELECT
            s1.id,
            s1.name,
            CAST(s1.amount AS REAL) AS current_amount,
            CAST(s2.amount AS REAL) AS previous_amount
        FROM RankedSites s1
        LEFT JOIN RankedSites s2
            ON s1.name = s2.name AND s2.rn = 2
        WHERE s1.rn = 1
        ORDER BY s1.name
    """)
    poker_sites_data = cur.fetchall()

    total_current = sum(site['current_amount'] for site in poker_sites_data)
    total_previous = sum(site['previous_amount'] if site['previous_amount'] is not None else 0 for site in poker_sites_data)

    cur.close()
    conn.close()
    return render_template("poker_sites.html", poker_sites=poker_sites_data, total_current=total_current, total_previous=total_previous)


@app.route("/assets")
def assets_page():
    """Assets page."""
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

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
        )
        SELECT
            a1.id,
            a1.name,
            CAST(a1.amount AS REAL) AS current_amount,
            CAST(a2.amount AS REAL) AS previous_amount,
            a1.currency
        FROM RankedAssets a1
        LEFT JOIN RankedAssets a2
            ON a1.name = a2.name AND a2.rn = 2
        WHERE a1.rn = 1
        ORDER BY a1.name
    """)
    assets_data = cur.fetchall()

    total_current = sum(asset['current_amount'] for asset in assets_data)
    total_previous = sum(asset['previous_amount'] if asset['previous_amount'] is not None else 0 for asset in assets_data)

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
    return render_template("assets.html", assets=assets_data, currencies=currencies, total_current=total_current, total_previous=total_previous)


@app.route("/add_asset", methods=["GET", "POST"])
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
        return redirect(url_for("assets_page"))
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


@app.route("/add_site", methods=["GET", "POST"])
def add_site():
    """Add a poker site."""
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

        last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cur.execute("INSERT INTO sites (name, amount, last_updated, currency) VALUES (%s, %s, %s, %s)", (name, amount, last_updated, currency_name))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("poker_sites_page"))
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
        return render_template("add_site.html", currencies=currencies)


@app.route("/update_asset/<string:asset_name>", methods=["GET", "POST"])
def update_asset(asset_name):
    """Update an asset."""
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == "POST":
        name = request.form.get("name", "").title()
        amount_str = request.form.get("amount", "")
        currency_name = request.form.get("currency", "USD")

        try:
            amount = float(amount_str)
            if amount <= 0:
                cur.close()
                conn.close()
                return redirect(url_for("assets_page"))
        except ValueError:
            cur.close()
            conn.close()
            return redirect(url_for("assets_page"))

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
        return redirect(url_for("assets_page"))
    else:
        cur.execute("SELECT * FROM assets WHERE name = %s ORDER BY last_updated DESC", (asset_name,))
        asset = cur.fetchone()
        if asset is None:
            cur.close()
            conn.close()
            return "Asset not found", 404
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
        return render_template("update_asset.html", asset=asset, currencies=currencies)


@app.route("/update_site/<string:site_name>", methods=["GET", "POST"])
def update_site(site_name):
    """Update a poker site."""
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == "POST":
        name = request.form.get("name", "").title()
        amount_str = request.form.get("amount", "")
        currency_name = request.form.get("currency", "USD")

        if not name or not amount_str:
            cur.close()
            conn.close()
            return redirect(url_for("poker_sites_page"))

        try:
            amount = float(amount_str)
            if amount <= 0:
                cur.close()
                conn.close()
                return redirect(url_for("poker_sites_page"))
        except ValueError:
            cur.close()
            conn.close()
            return redirect(url_for("poker_sites_page"))

        # Get the exchange rate for the selected currency
        cur.execute("SELECT rate FROM currency WHERE name = %s", (currency_name,))
        currency_rate_row = cur.fetchone()
        if currency_rate_row:
            exchange_rate = currency_rate_row['rate']
            amount_usd = amount / exchange_rate  # Convert to USD
        else:
            amount_usd = amount # Default to no conversion if currency not found

        last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cur.execute("INSERT INTO sites (name, amount, last_updated, currency) VALUES (%s, %s, %s, %s)", (name, amount_usd, last_updated, currency_name))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("poker_sites_page"))
    else:
        cur.execute("SELECT * FROM sites WHERE name = %s ORDER BY last_updated DESC", (site_name,))
        site = cur.fetchone()
        if site is None:
            cur.close()
            conn.close()
            return "Site not found", 404
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
        return render_template("update_site.html", site=site, currencies=currencies)


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
    cur = conn.cursor()
    if item_type == "site":
        cur.execute("DELETE FROM sites WHERE id = %s", (item_id,))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("poker_sites_page"))
    elif item_type == "asset":
        cur.execute("DELETE FROM assets WHERE id = %s", (item_id,))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("assets_page"))
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
    init_db()
    insert_initial_currency_data()
    app.run(debug=True)
