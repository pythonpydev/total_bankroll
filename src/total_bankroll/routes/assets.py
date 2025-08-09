from flask import Blueprint, render_template, redirect, request, url_for
import psycopg2
import psycopg2.extras
from db import get_db
from datetime import datetime

assets_bp = Blueprint("assets", __name__)

@assets_bp.route("/assets")
def assets_page():
    """Assets page."""
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

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

    total_current = sum(asset['current_amount'] for asset in assets_data)
    total_previous = sum(asset['previous_amount'] if asset['previous_amount'] is not None else 0 for asset in assets_data)

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
    return render_template("assets.html", assets=assets_data, currencies=currencies, total_current=total_current, total_previous=total_previous)

