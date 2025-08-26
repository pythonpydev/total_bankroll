from flask import Blueprint, render_template, redirect, request, url_for
from flask_security import login_required, current_user
from ..db import get_db
from datetime import datetime
from decimal import Decimal
import logging
import sys

logger = logging.getLogger(__name__)

poker_sites_bp = Blueprint("poker_sites", __name__)

@poker_sites_bp.route("/poker_sites")
@login_required
def poker_sites_page():
    """Poker Sites page."""
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT name, rate, symbol FROM currency")
    currency_data = cur.fetchall()
    currency_rates = {row['name']: row['rate'] for row in currency_data}
    currency_symbols = {row['name']: row['symbol'] for row in currency_data}

    # Get all sites for the user
    cur.execute("SELECT id, name FROM sites WHERE user_id = %s ORDER BY name", (current_user.id,))
    sites = cur.fetchall()

    poker_sites_data = []
    for site in sites:
        # Get the latest two history records for each site
        cur.execute("""
            SELECT amount, currency
            FROM site_history
            WHERE site_id = %s AND user_id = %s
            ORDER BY recorded_at DESC
            LIMIT 2
        """, (site['id'], current_user.id))
        history_records = cur.fetchall()

        current_amount = Decimal(0)
        previous_amount = Decimal(0)
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

        poker_sites_data.append({
            'id': site['id'],
            'name': site['name'],
            'current_amount': current_amount,
            'previous_amount': previous_amount,
            'currency': currency,
            'previous_currency': previous_currency,
            'current_amount_usd': current_amount_usd,
            'previous_amount_usd': previous_amount_usd,
            'currency_symbol': currency_symbols.get(currency, currency),
            'previous_currency_symbol': currency_symbols.get(previous_currency, previous_currency)
        })

    total_current = sum(site['current_amount_usd'] for site in poker_sites_data)
    total_previous = sum(site['previous_amount_usd'] for site in poker_sites_data)

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
    return render_template("poker_sites.html", poker_sites=poker_sites_data, currencies=currencies, total_current=total_current, total_previous=total_previous)


@poker_sites_bp.route("/add_site", methods=["GET", "POST"])
@login_required
def add_site():
    """Add a poker site."""
    conn = get_db()
    cur = conn.cursor()
    if request.method == "POST":
        name = request.form.get("name", "").title()
        amount_str = request.form.get("amount", "")
        currency_name = request.form.get("currency", "US Dollar")

        if not name or not amount_str:
            cur.close()
            conn.close()
            return "Name and amount are required", 400

        try:
            amount = round(float(amount_str), 2)
            if amount <= 0:
                cur.close()
                conn.close()
                return "Amount must be positive", 400
        except ValueError:
            cur.close()
            conn.close()
            return "Invalid amount format", 400

        # Insert into sites table
        cur.execute("INSERT INTO sites (name, user_id) VALUES (%s, %s)", (name, current_user.id))
        site_id = cur.lastrowid
        
        # Insert into site_history table
        recorded_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cur.execute("INSERT INTO site_history (site_id, amount, currency, recorded_at, user_id) VALUES (%s, %s, %s, %s, %s)", (site_id, amount, currency_name, recorded_at, current_user.id))
        
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("poker_sites.poker_sites_page"))
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
        print(f"DEBUG - Currencies fetched: {currencies}")  # testing
        cur.close()
        conn.close()
        return render_template("add_site.html", currencies=currencies)


@poker_sites_bp.route("/update_site/<int:site_id>", methods=["GET", "POST"])
@login_required
def update_site(site_id):
    """Update a poker site."""
    conn = get_db()
    cur = conn.cursor()
    if request.method == "POST":
        amount_str = request.form.get("amount", "")
        currency_name = request.form.get("currency", "US Dollar")

        if not amount_str:
            cur.close()
            conn.close()
            return redirect(url_for("poker_sites.poker_sites_page"))

        try:
            amount = round(float(amount_str), 2)
            if amount <= 0:
                cur.close()
                conn.close()
                return redirect(url_for("poker_sites.poker_sites_page"))
        except ValueError:
            cur.close()
            conn.close()
            return redirect(url_for("poker_sites.poker_sites_page"))

        recorded_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cur.execute("INSERT INTO site_history (site_id, amount, currency, recorded_at, user_id) VALUES (%s, %s, %s, %s, %s)", (site_id, amount, currency_name, recorded_at, current_user.id))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("poker_sites.poker_sites_page"))
    else:
        # Get latest site info
        cur.execute("SELECT id, name FROM sites WHERE id = %s AND user_id = %s", (site_id, current_user.id))
        site = cur.fetchone()
        if site is None:
            cur.close()
            conn.close()
            return "Site not found", 404

        # Get current amount and currency from site_history
        cur.execute("SELECT amount, currency FROM site_history WHERE site_id = %s AND user_id = %s ORDER BY recorded_at DESC LIMIT 1", (site_id, current_user.id))
        current_amount_row = cur.fetchone()
        current_amount = current_amount_row['amount'] if current_amount_row else Decimal(0)
        current_currency = current_amount_row['currency'] if current_amount_row else "US Dollar"

        # Get previous amount (second most recent entry)
        cur.execute("SELECT amount FROM site_history WHERE site_id = %s AND user_id = %s ORDER BY recorded_at DESC LIMIT 1, 1", (site_id, current_user.id))
        previous_amount_row = cur.fetchone()

        previous_amount = previous_amount_row['amount'] if previous_amount_row else Decimal(0)

        # Fetch currencies
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
        return render_template("update_site.html", site=site, currencies=currencies, previous_amount=previous_amount, current_amount=current_amount, current_currency=current_currency)

@poker_sites_bp.route("/rename_site/<int:site_id>", methods=["GET", "POST"])
@login_required
def rename_site(site_id):
    """Rename a poker site."""
    conn = get_db()
    cur = conn.cursor()
    if request.method == "POST":
        new_name = request.form.get("new_name", "").title()
        if not new_name:
            cur.close()
            conn.close()
            return "New name is required", 400

        cur.execute("UPDATE sites SET name = %s WHERE id = %s AND user_id = %s", (new_name, site_id, current_user.id))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("poker_sites.poker_sites_page"))
    else:
        cur.execute("SELECT id, name FROM sites WHERE id = %s AND user_id = %s", (site_id, current_user.id))
        site = cur.fetchone()
        if site is None:
            cur.close()
            conn.close()
            return "Site not found", 404
        cur.close()
        conn.close()
        return render_template("rename_site.html", site=site)
