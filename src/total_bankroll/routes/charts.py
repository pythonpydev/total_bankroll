from flask import Blueprint, render_template, jsonify, current_app
from ..db import get_db
from datetime import datetime

charts_bp = Blueprint("charts", __name__)

@charts_bp.route("/charts")
def charts_page():
    """Charts page."""
    return render_template("charts.html")

@charts_bp.route("/charts/poker_sites/line")
def poker_sites_line_chart_page():
    """Poker Sites Line Chart page."""
    return render_template("poker_sites_line_chart.html")

@charts_bp.route("/charts/poker_sites/bar")
def poker_sites_bar_chart_page():
    """Poker Sites Bar Chart page."""
    return render_template("poker_sites_bar_chart.html")

@charts_bp.route("/charts/poker_sites/pie")
def poker_sites_pie_chart_page():
    """Poker Sites Pie Chart page."""
    return render_template("poker_sites_pie_chart.html")

@charts_bp.route("/charts/poker_sites/polar_area")
def poker_sites_polar_area_chart_page():
    """Poker Sites Polar Area Chart page."""
    return render_template("poker_sites_polar_area_chart.html")

@charts_bp.route("/charts/poker_sites/radar")
def poker_sites_radar_chart_page():
    """Poker Sites Radar Chart page."""
    return render_template("poker_sites_radar_chart.html")

@charts_bp.route("/charts/poker_sites/scatter")
def poker_sites_scatter_chart_page():
    """Poker Sites Scatter Chart page."""
    return render_template("poker_sites_scatter_chart.html")

@charts_bp.route("/charts/assets/line")
def assets_line_chart_page():
    """Assets Line Chart page."""
    return render_template("assets_line_chart.html")

@charts_bp.route("/charts/assets/bar")
def assets_bar_chart_page():
    """Assets Bar Chart page."""
    return render_template("assets_bar_chart.html")

@charts_bp.route("/charts/assets/scatter")
def assets_scatter_chart_page():
    """Assets Scatter Chart page."""
    return render_template("assets_scatter_chart.html")

@charts_bp.route("/charts/bankroll/line")
def bankroll_line_chart_page():
    """Bankroll Line Chart page."""
    return render_template("bankroll_line_chart.html")

@charts_bp.route("/charts/bankroll/bar")
def bankroll_bar_chart_page():
    """Bankroll Bar Chart page."""
    return render_template("bankroll_bar_chart.html")

@charts_bp.route("/charts/profit/line")
def profit_line_chart_page():
    """Profit Line Chart page."""
    return render_template("profit_line_chart.html")

@charts_bp.route("/charts/profit/bar")
def profit_bar_chart_page():
    """Profit Bar Chart page."""
    return render_template("profit_bar_chart.html")

@charts_bp.route("/charts/withdrawals/line")
def withdrawals_line_chart_page():
    """Withdrawals Line Chart page."""
    return render_template("withdrawals_line_chart.html")

@charts_bp.route("/charts/withdrawals/bar")
def withdrawals_bar_chart_page():
    """Withdrawals Bar Chart page."""
    return render_template("withdrawals_bar_chart.html")

@charts_bp.route("/charts/poker_sites_data")
def get_poker_sites_data():
    try:
        conn = get_db()
        cur = conn.cursor()

        # Get all unique poker site names
        cur.execute("SELECT DISTINCT name FROM sites ORDER BY name")
        site_names = [row['name'] for row in cur.fetchall()]

        # Get the latest data for each poker site
        cur.execute("""
            SELECT
                s.name,
                s.amount,
                s.currency
            FROM sites s
            INNER JOIN (
                SELECT
                    name,
                    MAX(last_updated) AS max_last_updated
                FROM sites
                GROUP BY name
            ) AS latest_sites
            ON s.name = latest_sites.name AND s.last_updated = latest_sites.max_last_updated
        """)
        raw_data = cur.fetchall()

        # Get currency exchange rates
        cur.execute("SELECT name, rate FROM currency")
        currency_rates = {row['name']: row['rate'] for row in cur.fetchall()}

        cur.close()

        # Process data for charting
        labels = []
        data = []

        for row in raw_data:
            # Convert amount to USD
            amount_usd = float(row['amount']) / float(currency_rates.get(row['currency'], 1.0))
            labels.append(row['name'])
            data.append(amount_usd)

        # Prepare data for Chart.js
        datasets = [{
            'label': 'Latest Amount (USD)',
            'data': data,
            'backgroundColor': [
                'rgba(255, 99, 132, 0.6)',
                'rgba(54, 162, 235, 0.6)',
                'rgba(255, 206, 86, 0.6)',
                'rgba(75, 192, 192, 0.6)',
                'rgba(153, 102, 255, 0.6)',
                'rgba(255, 159, 64, 0.6)'
            ],
            'borderColor': [
                'rgba(255, 99, 132, 1)',
                'rgba(54, 162, 235, 1)',
                'rgba(255, 206, 86, 1)',
                'rgba(75, 192, 192, 1)',
                'rgba(153, 102, 255, 1)',
                'rgba(255, 159, 64, 1)'
            ],
            'borderWidth': 1
        }]

        return jsonify({
            'labels': labels,
            'datasets': datasets
        })
    except Exception as e:
        current_app.logger.error(f"Error in get_poker_sites_data: {e}")
        return jsonify({'error': str(e)}), 500

@charts_bp.route("/charts/poker_sites_historical_data")
def get_poker_sites_historical_data():
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
        # Group data by site name
        processed_data = {name: [] for name in site_names}
        min_date = None
        max_date = None

        for row in raw_data:
            date_obj = row['last_updated'] # Assuming this is already a datetime object from PyMySQL
            date_str = date_obj.strftime("%Y-%m-%d")
            amount_usd = float(row['amount']) / float(currency_rates.get(row['currency'], 1.0))
            processed_data[row['name']].append({'x': date_str, 'y': amount_usd})

            if min_date is None or date_obj < min_date:
                min_date = date_obj
            if max_date is None or date_obj > max_date:
                max_date = date_obj

        # Prepare data for Chart.js
        datasets = []
        colors = [
            'rgba(255, 99, 132, 0.8)',  # Red
            'rgba(54, 162, 235, 0.8)',  # Blue
            'rgba(255, 206, 86, 0.8)',  # Yellow
            'rgba(75, 192, 192, 0.8)',  # Green
            'rgba(153, 102, 255, 0.8)', # Purple
            'rgba(255, 159, 64, 0.8)'   # Orange
        ]
        border_colors = [
            'rgba(255, 99, 132, 1)',
            'rgba(54, 162, 235, 1)',
            'rgba(255, 206, 86, 1)',
            'rgba(75, 192, 192, 1)',
            'rgba(153, 102, 255, 1)',
            'rgba(255, 159, 64, 1)'
        ]

        for i, site_name in enumerate(site_names):
            datasets.append({
                'label': site_name,
                'data': processed_data[site_name],
                'borderColor': border_colors[i % len(border_colors)],
                'fill': False
            })

        return jsonify({
            'labels': site_names, # Labels are not directly used for scatter, but can be for legend
            'datasets': datasets,
            'min_date': min_date.strftime("%Y-%m-%d") if min_date else None,
            'max_date': max_date.strftime("%Y-%m-%d") if max_date else None
        })
    except Exception as e:
        current_app.logger.error(f"Error in get_poker_sites_historical_data: {e}")
        print(f"Error in get_poker_sites_historical_data: {e}") # Added for debugging
        return jsonify({'error': str(e)}), 500

@charts_bp.route("/charts/assets_data")
def get_assets_data():
    try:
        conn = get_db()
        cur = conn.cursor()

        # Get all unique asset names
        cur.execute("SELECT DISTINCT name FROM assets ORDER BY name")
        asset_names = [row['name'] for row in cur.fetchall()]

        # Get all historical data for assets
        cur.execute("""
            SELECT
                last_updated,
                name,
                amount,
                currency
            FROM assets
            ORDER BY last_updated, name
        """)
        raw_data = cur.fetchall()

        # Get currency exchange rates
        cur.execute("SELECT name, rate FROM currency")
        currency_rates = {row['name']: row['rate'] for row in cur.fetchall()}

        cur.close()

        # Process data for charting
        processed_data = {}
        for row in raw_data:
            date_str = row['last_updated'].strftime("%Y-%m-%d")
            if date_str not in processed_data:
                processed_data[date_str] = {name: 0.0 for name in asset_names}

            amount_usd = float(row['amount']) / float(currency_rates.get(row['currency'], 1.0))
            processed_data[date_str][row['name']] = amount_usd

        # Prepare data for Chart.js
        labels = sorted(processed_data.keys())
        datasets = []

        for asset_name in asset_names:
            data = [processed_data[date][asset_name] for date in labels]
            datasets.append({
                'label': asset_name,
                'data': data,
                'fill': False
            })

        return jsonify({
            'labels': labels,
            'datasets': datasets
        })
    except Exception as e:
        current_app.logger.error(f"Error in get_withdrawals_data: {e}")
        return jsonify({'error': str(e)}), 500

@charts_bp.route("/charts/deposits_data")
def get_deposits_data():
    try:
        conn = get_db()
        cur = conn.cursor()

        # Get all historical data for deposits
        cur.execute("""
            SELECT
                d.last_updated,
                SUM(d.amount / c.rate) AS total_usd
            FROM deposits d
            JOIN currency c ON d.currency = c.name
            GROUP BY d.last_updated
            ORDER BY d.last_updated
        """)
        raw_data = cur.fetchall()

        cur.close()

        labels = [row['last_updated'].strftime("%Y-%m-%d") for row in raw_data]
        data = [float(row['total_usd']) for row in raw_data]

        datasets = [{
            'label': 'Total Deposits (USD)',
            'data': data,
            'fill': False,
            'borderColor': 'rgb(54, 162, 235)',
            'tension': 0.1
        }]

        return jsonify({
            'labels': labels,
            'datasets': datasets
        })
    except Exception as e:
        current_app.logger.error(f"Error in get_deposits_data: {e}")
        return jsonify({'error': str(e)}), 500

@charts_bp.route("/charts/profit_data")
def get_profit_data():
    try:
        conn = get_db()
        cur = conn.cursor()

        # Get historical data for total bankroll, deposits, and withdrawals
        cur.execute("""
            SELECT
                t.last_updated,
                SUM(CASE WHEN t.type = 'bankroll' THEN t.amount_usd ELSE 0 END) AS total_bankroll,
                SUM(CASE WHEN t.type = 'deposits' THEN t.amount_usd ELSE 0 END) AS total_deposits,
                SUM(CASE WHEN t.type = 'withdrawals' THEN t.amount_usd ELSE 0 END) AS total_withdrawals
            FROM (
                SELECT last_updated, (amount / c.rate) AS amount_usd, 'bankroll' AS type FROM sites JOIN currency c ON sites.currency = c.name
                UNION ALL
                SELECT last_updated, (amount / c.rate) AS amount_usd, 'bankroll' AS type FROM assets JOIN currency c ON assets.currency = c.name
                UNION ALL
                SELECT last_updated, (amount / c.rate) AS amount_usd, 'deposits' AS type FROM deposits JOIN currency c ON deposits.currency = c.name
                UNION ALL
                SELECT last_updated, (amount / c.rate) AS amount_usd, 'withdrawals' AS type FROM drawings JOIN currency c ON drawings.currency = c.name
            ) AS t
            GROUP BY t.last_updated
            ORDER BY t.last_updated
        """)
        raw_data = cur.fetchall()

        cur.close()

        labels = [row['last_updated'].strftime("%Y-%m-%d") for row in raw_data]
        profit_data = []

        for row in raw_data:
            bankroll = float(row['total_bankroll'])
            deposits = float(row['total_deposits'])
            withdrawals = float(row['total_withdrawals'])
            profit = bankroll - deposits + withdrawals
            profit_data.append(profit)

        datasets = [{
            'label': 'Profit (USD)',
            'data': profit_data,
            'fill': False,
            'borderColor': 'rgb(255, 99, 132)',
            'tension': 0.1
        }]

        return jsonify({
            'labels': labels,
            'datasets': datasets
        })
    except Exception as e:
        current_app.logger.error(f"Error in get_profit_data: {e}")
        return jsonify({'error': str(e)}), 500