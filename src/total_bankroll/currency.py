from .db import get_db
import click
from flask.cli import with_appcontext

def insert_initial_currency_data(app):
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

@click.command('init-currency')
@with_appcontext
def init_currency_command():
    """Add initial currency data to the database."""
    from flask import current_app
    insert_initial_currency_data(current_app)
    click.echo('Initialized the currency data.')