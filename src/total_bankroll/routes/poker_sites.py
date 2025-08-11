from flask import Blueprint, render_template
import psycopg2
import psycopg2.extras

from db import get_db

poker_sites_bp = Blueprint("poker_sites", __name__)

@poker_sites_bp.route("/poker_sites")
def poker_sites_page():
    """Poker Sites page."""
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cur.execute("SELECT name, rate, symbol FROM currency")
    currency_data = cur.fetchall()
    currency_rates = {row['name']: row['rate'] for row in currency_data}
    currency_symbols = {row['name']: row['symbol'] for row in currency_data}

    # Get current and previous asset totals
    cur.execute("""
        WITH RankedSites AS (
            SELECT
                id,
                name,
                amount,
                last_updated,
                currency,
                ROW_NUMBER() OVER (PARTITION BY name ORDER BY last_updated DESC) as rn
            FROM sites
        )
        SELECT
            s1.id,
            s1.name,
            s1.amount AS current_amount,
            s2.amount AS previous_amount,
            s1.currency,
            s2.currency AS previous_currency
        FROM RankedSites s1
        LEFT JOIN RankedSites s2
            ON s1.name = s2.name AND s2.rn = 2
        WHERE s1.rn = 1
        ORDER BY s1.name
    """)

    poker_sites_data_raw = cur.fetchall()

    poker_sites_data = []
    for site in poker_sites_data_raw:
        converted_site = dict(site)
        original_amount = converted_site['current_amount']
        original_previous_amount = converted_site['previous_amount']
        currency = converted_site['currency']
        previous_currency = converted_site['previous_currency']

        rate = currency_rates.get(currency, 1.0)
        previous_rate = currency_rates.get(previous_currency, 1.0)

        converted_site['current_amount_usd'] = original_amount / rate
        converted_site['previous_amount_usd'] = original_previous_amount / previous_rate if original_previous_amount is not None else 0.0
        
        # Add currency symbols to the site data
        converted_site['currency_symbol'] = currency_symbols.get(currency, currency)
        converted_site['previous_currency_symbol'] = currency_symbols.get(previous_currency, previous_currency) if previous_currency else None
        
        poker_sites_data.append(converted_site)

    total_current = sum(site['current_amount_usd'] for site in poker_sites_data)
    total_previous = sum(site['previous_amount_usd'] if site['previous_amount_usd'] is not None else 0 for site in poker_sites_data)

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