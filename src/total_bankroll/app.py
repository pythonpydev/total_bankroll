"""Web entry point for total_bankroll."""

from flask import Flask, Blueprint, render_template, request, redirect, url_for
import os
from dotenv import load_dotenv
from total_bankroll.config import config

load_dotenv() # Load environment variables from .env file

import psycopg2
import psycopg2.extras
from datetime import datetime

from . import currency 
from .db import get_db, close_db
from .routes.home import home_bp
from .routes.poker_sites import poker_sites_bp 
from .routes.assets import assets_bp
from .routes.update_poker_site import update_site_bp
from .routes.withdrawal import withdrawal_bp
from .routes.deposit import deposit_bp   
from .routes.add_deposit import add_deposit_bp
from .routes.add_withdrawal import add_withdrawal_bp
from .routes.settings import settings_bp
from .routes.settings import reset_db_bp
from .routes.settings import export_db_bp
from .routes.settings import import_db_bp
from .routes.currency_update import currency_update_bp

app = Flask(__name__)
app.config.from_object(config[os.getenv('FLASK_ENV', 'default')])

# Close db after each request
app.teardown_appcontext(close_db)

# Register blueprints
app.register_blueprint(home_bp)
app.register_blueprint(poker_sites_bp)
app.register_blueprint(assets_bp)
app.register_blueprint(update_site_bp)
app.register_blueprint(withdrawal_bp)
app.register_blueprint(deposit_bp)
app.register_blueprint(add_deposit_bp)
app.register_blueprint(add_withdrawal_bp)
app.register_blueprint(settings_bp)
app.register_blueprint(reset_db_bp)
app.register_blueprint(export_db_bp)
app.register_blueprint(import_db_bp)
app.register_blueprint(currency_update_bp)

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
        return redirect(url_for("withdrawal.withdrawal"))
        
    elif item_type == "deposit":
        cur.execute("DELETE FROM deposits WHERE id = %s", (item_id,))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("deposit.deposit"))
        
    else:
        cur.close()
        conn.close()
        return "Invalid item type", 400


@app.route("/about")
def about_page():
    """About page."""
    return render_template("about.html")


if __name__ == "__main__":
    currency.insert_initial_currency_data(app)
    app.run(debug=True, port=5001)