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

@charts_bp.route("/charts/bankroll/pie")
def bankroll_pie_chart_page():
    """Bankroll Pie Chart page."""
    return render_template("bankroll_pie_chart.html")

@charts_bp.route("/charts/bankroll/polar_area")
def bankroll_polar_area_chart_page():
    """Bankroll Polar Area Chart page."""
    return render_template("bankroll_polar_area_chart.html")

@charts_bp.route("/charts/bankroll/radar")
def bankroll_radar_chart_page():
    """Bankroll Radar Chart page."""
    return render_template("bankroll_radar_chart.html")

@charts_bp.route("/charts/bankroll/scatter")
def bankroll_scatter_chart_page():
    """Bankroll Scatter Chart page."""
    return render_template("bankroll_scatter_chart.html")

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