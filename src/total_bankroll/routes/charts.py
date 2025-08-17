from flask import Blueprint, render_template, jsonify, current_app
from ..db import get_db
from datetime import datetime

charts_bp = Blueprint("charts", __name__)

@charts_bp.route("/charts")
def charts_page():
    """Charts page."""
    return render_template("charts.html")

@charts_bp.route("/charts/poker_sites")
def poker_sites_chart_page():
    """Poker Sites Chart page."""
    return render_template("poker_sites_chart.html")

@charts_bp.route("/charts/poker_sites_data")
def get_poker_sites_data():
    try:
        conn = get_db()
        cur = conn.cursor()

        # Get all unique poker site names
        cur.execute("SELECT DISTINCT name FROM sites ORDER BY name")
        site_names = [row['name'] for row in cur.fetchall()]

        # Get all historical data for poker sites
        cur.execute("""
            SELECT
                last_updated,
                name,
                amount,
                currency
            FROM sites
            ORDER BY last_updated, name
        """)
        raw_data = cur.fetchall()

        # Get currency exchange rates
        cur.execute("SELECT name, rate FROM currency")
        currency_rates = {row['name']: row['rate'] for row in cur.fetchall()}

        cur.close()

        # Process data for charting
        # Group data by date and then by site
        processed_data = {}
        for row in raw_data:
            date_str = row['last_updated'].strftime("%Y-%m-%d")
            if date_str not in processed_data:
                processed_data[date_str] = {name: 0.0 for name in site_names}

            # Convert amount to USD
            amount_usd = float(row['amount']) / float(currency_rates.get(row['currency'], 1.0))
            processed_data[date_str][row['name']] = amount_usd

        # Prepare data for Chart.js
        labels = sorted(processed_data.keys())
        datasets = []

        for site_name in site_names:
            data = [processed_data[date][site_name] for date in labels]
            datasets.append({
                'label': site_name,
                'data': data,
                'fill': False
            })

        return jsonify({
            'labels': labels,
            'datasets': datasets
        })
    except Exception as e:
        current_app.logger.error(f"Error in get_poker_sites_data: {e}")
        return jsonify({'error': str(e)}), 500