from flask import Blueprint, render_template
import psycopg2
import psycopg2.extras

from db import get_db

home_bp = Blueprint("home", __name__)

@home_bp.route("/")
def home():
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

