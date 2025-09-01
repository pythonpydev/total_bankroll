import click
from flask.cli import with_appcontext
import requests
from datetime import date
from .extensions import db
from .models import Currency
from flask import current_app


def register_commands(app):
    """Register CLI commands with the Flask app."""
    app.cli.add_command(update_rates_command)


@click.command(name='update_rates')
@with_appcontext
def update_rates_command():
    """
    Fetches and updates currency exchange rates from an API.
    Intended to be run daily, but will only perform the update on the 1st of the month.
    """
    # Check if it's the first day of the month
    if date.today().day != 1:
        message = "Not the first day of the month. Skipping update."
        current_app.logger.info(message)
        click.echo(message)
        return

    click.echo("First day of the month! Starting exchange rate update...")
    api_key = current_app.config.get("EXCHANGE_RATE_API_KEY")
    if not api_key:
        current_app.logger.error("Exchange rate API key not configured.")
        click.echo("Error: Exchange rate API key not configured. Set EXCHANGE_RATE_API_KEY.", err=True)
        return

    base_currency = "USD"
    api_url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/{base_currency}"

    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("result") != "success":
            error_message = data.get("error-type", "Unknown API error")
            current_app.logger.error(f"API error: {error_message}")
            click.echo(f"Error: Failed to retrieve exchange rates: {error_message}", err=True)
            return

        rates = data.get("conversion_rates")
        if not rates:
            current_app.logger.error("No conversion rates found in API response")
            click.echo("Error: No conversion rates found in API response.", err=True)
            return

        existing_currencies = {c.code: c for c in db.session.query(Currency).all()}
        updated_count = 0
        for code, rate in rates.items():
            if code in existing_currencies:
                existing_currencies[code].rate = rate
                updated_count += 1
        
        db.session.commit()
        message = f"Successfully updated {updated_count} exchange rates!"
        current_app.logger.info(message)
        click.echo(message)

    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Error fetching exchange rates: {e}")
        click.echo(f"Error fetching exchange rates: {e}", err=True)
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Unexpected error during rate update: {e}")
        click.echo(f"An unexpected error occurred: {e}", err=True)