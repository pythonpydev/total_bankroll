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
    cur.execute("""
        WITH RankedSites AS (
            SELECT
                id,
                name,
                amount,
                last_updated,
                ROW_NUMBER() OVER (PARTITION BY name ORDER BY last_updated DESC) as rn
            FROM sites
        )
        SELECT
            s1.id,
            s1.name,
            CAST(s1.amount AS REAL) AS current_amount,
            CAST(s2.amount AS REAL) AS previous_amount
        FROM RankedSites s1
        LEFT JOIN RankedSites s2
            ON s1.name = s2.name AND s2.rn = 2
        WHERE s1.rn = 1
        ORDER BY s1.name
    """)
    poker_sites_data = cur.fetchall()

    total_current = sum(site['current_amount'] for site in poker_sites_data)
    total_previous = sum(site['previous_amount'] if site['previous_amount'] is not None else 0 for site in poker_sites_data)

    cur.close()
    conn.close()
    return render_template("poker_sites.html", poker_sites=poker_sites_data, total_current=total_current, total_previous=total_previous)
