import os
import click
import requests
from flask import current_app
from flask.cli import with_appcontext
from .extensions import db

from .models import Currency
def fetch_exchange_rates(api_key):
    """Fetch live exchange rates from ExchangeRate-API."""
    url = f"https://v6.exchangerate-api.com/v6/{api_key} /latest/USD"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()
        if data.get("result") != "success":
            raise ValueError("API response indicates failure")
        return data.get("conversion_rates")
    except (requests.RequestException, ValueError) as e:
        current_app.logger.error(f"Failed to fetch exchange rates: {e}")
        return None
def get_fallback_currencies():
    """Return static currency data from CSV as fallback."""
    return [
        ('US Dollar', 1.0, 'USD', '$'),
        ('British Pound', 0.7377, 'GBP', '£'),
        ('Euro', 0.8545, 'EUR', '€'),
        ('Chinese Yuan', 7.188, 'CNY', '¥'),
        ('Japanese Yen', 147.2455, 'JPY', '¥'),
        ('Canadian Dollar', 1.3815, 'CAD', 'C$'),
        ('Australian Dollar', 1.5362, 'AUD', 'A$'),
        ('Swiss Franc', 0.8066, 'CHF', 'CHF'),
        ('New Zealand Dollar', 1.6874, 'NZD', 'NZ$'),
        ('Swedish Krona', 9.5536, 'SEK', 'kr'),
        ('Norwegian Krone', 10.1817, 'NOK', 'kr'),
        ('Danish Krone', 6.3742, 'DKK', 'kr'),
    ]
def insert_initial_currency_data():
    """Insert or update currency data with live exchange rates or fallback to static data."""
    print("insert_initial_currency_data called")
    print(f"Currency table count: {db.session.query(Currency).count()}")
    
    # Check if table is empty
    if db.session.query(Currency).count() == 0:
        # Fetch live exchange rates
        api_key = os.getenv("EXCHANGE_RATE_API_KEY")  # Store API key in environment variable
        rates = fetch_exchange_rates(api_key)
        if rates:
            # Map API rates to your currency list
            currency_mapping = {
                'USD': ('US Dollar', '$'),
                'GBP': ('British Pound', '£'),
                'EUR': ('Euro', '€'),
                'CNY': ('Chinese Yuan', '¥'),
                'JPY': ('Japanese Yen', '¥'),
                'CAD': ('Canadian Dollar', 'C$'),
                'AUD': ('Australian Dollar', 'A$'),
                'CHF': ('Swiss Franc', 'CHF'),
                'NZD': ('New Zealand Dollar', 'NZ$'),
                'SEK': ('Swedish Krona', 'kr'),
                'NOK': ('Norwegian Krone', 'kr'),
                'DKK': ('Danish Krone', 'kr'),
            }
            currencies_to_add = []
            for code, (name, symbol) in currency_mapping.items():
                if code in rates:  
                    currencies_to_add.append(Currency(name=name, rate=rates.get(code, 1.0), code=code, symbol=symbol))
        else:
            # Fallback to static CSV data
            current_app.logger.warning("Using fallback currency data from CSV")
            currencies_to_add = []
            for name, rate, code, symbol in get_fallback_currencies():
                currencies_to_add.append(Currency(name=name, rate=rate, code=code, symbol=symbol))
        # Insert data into the database
        try:
            db.session.add_all(currencies_to_add)
            db.session.commit()
            current_app.logger.info(f"Inserted {len (currencies_to_add)} currencies into the database")
        except Exception as e:
            current_app.logger.error(f"Database error: {e}" )
            db.session.rollback()
@click.command('init-currency')
@with_appcontext
def init_currency_command():
    """Add initial currency data to the database."""
    insert_initial_currency_data()
    click.echo('Initialized the currency data.')
