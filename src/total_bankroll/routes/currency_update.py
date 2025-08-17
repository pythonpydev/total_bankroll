from flask import Blueprint, render_template, redirect, url_for, flash, current_app
import requests
import pymysql
from ..db import get_db

currency_update_bp = Blueprint("currency_update", __name__)

@currency_update_bp.route("/update_exchange_rates", methods=["POST"])
def update_exchange_rates():
    api_key = current_app.config.get("EXCHANGE_RATE_API_KEY") # Get API key from environment variable
    if not api_key:
        flash("Exchange rate API key not configured. Please set the EXCHANGE_RATE_API_KEY environment variable.", "danger")
        return redirect(url_for("currencies"))

    base_currency = "USD" # ExchangeRate-API free tier uses USD as base
    api_url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/{base_currency}"

    try:
        response = requests.get(api_url)
        response.raise_for_status() # Raise an exception for HTTP errors
        data = response.json()
        rates = data.get("conversion_rates")

        if not rates:
            flash("Failed to retrieve exchange rates from API. No conversion rates found.", "danger")
            return redirect(url_for("currencies"))

        conn = get_db()
        cur = conn.cursor()

        for code, rate in rates.items():
            # Only update currencies that are already in our database
            # We assume the initial currency data populates the necessary currencies
            # and we only update their rates.
            # If you want to add new currencies from the API, you'd need to fetch
            # their names and symbols, which this API doesn't directly provide in this endpoint.

            # UPSERT logic: Try to insert, if conflict on 'code', then update 'rate'
            # Note: 'name' and 'symbol' are not provided by this API endpoint, so we only update 'rate'.
            # If a currency from the API is not in our DB, it won't be inserted here.
            upsert_sql = """
                INSERT INTO currency (name, rate, code, symbol)
                VALUES (NULL, %s, %s, NULL) -- Name and symbol will be updated if conflict, or remain NULL if new
                ON CONFLICT (code) DO UPDATE SET
                    rate = EXCLUDED.rate;
            """
            # The above UPSERT is problematic because 'name' and 'symbol' are NOT NULL.
            # We should only update existing entries or insert with full data.
            # Since this API only gives code and rate, we should only update existing ones.

            # Let's use a simple UPDATE statement for existing currencies.
            # This assumes that all currencies we care about are already in our 'currency' table.
            cur.execute("UPDATE currency SET rate = %s WHERE code = %s;", (rate, code))

        conn.commit()
        cur.close()
        conn.close()
        flash("Exchange rates updated successfully!", "success")

    except requests.exceptions.RequestException as e:
        flash(f"Error fetching exchange rates: {e}", "danger")
    except Exception as e:
        flash(f"An unexpected error occurred: {e}", "danger")

    return redirect(url_for("currencies"))