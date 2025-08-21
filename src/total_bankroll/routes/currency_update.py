from flask import Blueprint, render_template, redirect, url_for, flash, current_app
import requests
import pymysql
from ..db import get_db

currency_update_bp = Blueprint("currency_update", __name__)

@currency_update_bp.route("/currencies")
def currencies_page():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT name, code, symbol, rate, updated_at FROM currency ORDER BY name")
    currencies = cur.fetchall()
    cur.close()
    return render_template("currencies.html", currencies=currencies)

@currency_update_bp.route("/update_exchange_rates", methods=["POST"])
def update_exchange_rates():
    api_key = current_app.config.get("EXCHANGE_RATE_API_KEY")
    if not api_key:
        current_app.logger.error("Exchange rate API key not configured")
        flash("Exchange rate API key not configured. Please set the EXCHANGE_RATE_API_KEY environment variable.", "danger")
        return redirect(url_for("currency_update.currencies_page"))

    base_currency = "USD"
    api_url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/{base_currency}"

    try:
        # Fetch exchange rates
        response = requests.get(api_url, timeout=5)
        response.raise_for_status()
        data = response.json()

        if data.get("result") != "success":
            error_message = data.get("error-type", "Unknown API error")
            current_app.logger.error(f"API error: {error_message}")
            flash(f"Failed to retrieve exchange rates: {error_message}", "danger")
            return redirect(url_for("currency_update.currencies_page"))

        rates = data.get("conversion_rates")
        if not rates:
            current_app.logger.error("No conversion rates found in API response")
            flash("Failed to retrieve exchange rates: No conversion rates found.", "danger")
            return redirect(url_for("currency_update.currencies_page"))

        # Get existing currency codes from the database
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT code FROM currency")
        existing_codes = {row["code"] for row in cur.fetchall()}

        # Update rates for existing currencies
        updated_count = 0
        for code, rate in rates.items():
            if code in existing_codes:
                cur.execute(
                    "UPDATE currency SET rate = %s, updated_at = CURRENT_TIMESTAMP WHERE code = %s",
                    (rate, code)
                )
                current_app.logger.info(f"Updated {code} with rate {rate}")
                updated_count += cur.rowcount

        conn.commit()
        cur.close()
        # Note: Avoid closing conn if get_db() manages it in the app context
        # conn.close()

        if updated_count > 0:
            flash(f"Successfully updated {updated_count} exchange rates!", "success")
        else:
            flash("No exchange rates were updated. Ensure currencies exist in the database.", "warning")

    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Error fetching exchange rates: {e}")
        flash(f"Error fetching exchange rates: {e}", "danger")
    except pymysql.Error as e:
        current_app.logger.error(f"Database error: {e}")
        flash(f"Database error occurred: {e}", "danger")
        conn.rollback()
    except Exception as e:
        current_app.logger.error(f"Unexpected error: {e}")
        flash(f"An unexpected error occurred: {e}", "danger")

    return redirect(url_for("currency_update.currencies_page"))