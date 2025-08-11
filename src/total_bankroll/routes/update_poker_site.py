from flask import Blueprint, render_template, redirect, request, url_for
import psycopg2
import psycopg2.extras
from db import get_db
from datetime import datetime

update_site_bp = Blueprint("update_site", __name__)

@update_site_bp.route("/update_site/<string:site_name>", methods=["GET", "POST"])
def update_site(site_name):
    """Update a poker site."""
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == "POST":
        name = request.form.get("name", "").title()
        amount_str = request.form.get("amount", "")
        currency_name = request.form.get("currency", "US Dollar")

        if not name or not amount_str:
            cur.close()
            conn.close()
            return redirect(url_for("poker_sites_page"))

        try:
            amount = float(amount_str)
            if amount <= 0:
                cur.close()
                conn.close()
                return redirect(url_for("poker_sites_page"))
        except ValueError:
            cur.close()
            conn.close()
            return redirect(url_for("poker_sites_page"))

        last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cur.execute("INSERT INTO sites (name, amount, last_updated, currency) VALUES (%s, %s, %s, %s)", (name, amount, last_updated, currency_name))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("poker_sites.poker_sites_page"))
    else:
        cur.execute("SELECT * FROM sites WHERE name = %s ORDER BY last_updated DESC", (site_name,))
        site = cur.fetchone()
        if site is None:
            cur.close()
            conn.close()
            return "Site not found", 404

        cur.execute("SELECT amount FROM sites WHERE name = %s ORDER BY last_updated DESC OFFSET 1 LIMIT 1", (site_name,))
        previous_amount_row = cur.fetchone()
        previous_amount = previous_amount_row[0] if previous_amount_row else None

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
        return render_template("update_site.html", site=site, currencies=currencies, previous_amount=previous_amount)
