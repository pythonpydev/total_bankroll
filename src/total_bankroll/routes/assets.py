from flask import Blueprint, render_template, redirect, request, url_for
import psycopg2
import psycopg2.extras
from ..db import get_db
from datetime import datetime

assets_bp = Blueprint("assets", __name__)

@assets_bp.route("/assets")
def assets_page():
    """Assets page."""
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

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
    """)
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
        converted_asset['previous_amount_usd'] = original_previous_amount / previous_rate if original_previous_amount is not None else 0.0
        
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