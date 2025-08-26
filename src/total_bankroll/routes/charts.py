from flask import Blueprint, render_template, jsonify, current_app
from flask_security import current_user, login_required
from ..db import get_db
from datetime import datetime, timedelta
from decimal import Decimal

charts_bp = Blueprint("charts", __name__)

@charts_bp.route("/charts")
@login_required
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

@charts_bp.route("/charts/assets/pie")
def assets_pie_chart_page():
    """Assets Pie Chart page."""
    return render_template("assets_pie_chart.html")

@charts_bp.route("/charts/assets/polar_area")
def assets_polar_area_chart_page():
    """Assets Polar Area Chart page."""
    return render_template("assets_polar_area_chart.html")

@charts_bp.route("/charts/assets/radar")
def assets_radar_chart_page():
    """Assets Radar Chart page."""
    return render_template("assets_radar_chart.html")

@charts_bp.route("/charts/bankroll/line")
def bankroll_line_chart_page():
    """Bankroll Line Chart page."""
    return render_template("bankroll_line_chart.html")

@charts_bp.route("/charts/bankroll/bar")
def bankroll_bar_chart_page():
    """Bankroll Bar Chart page."""
    return render_template("bankroll_bar_chart.html")

@charts_bp.route("/charts/bankroll/data")
@login_required
def get_bankroll_data():
    try:
        conn = get_db()
        cur = conn.cursor()

        # Get currency rates
        cur.execute("SELECT name, rate FROM currency")
        currency_rates = {row['name']: Decimal(str(row['rate'])) for row in cur.fetchall()}

        # Get all site history
        cur.execute("""
            SELECT sh.site_id, sh.amount, sh.currency, sh.recorded_at, s.name
            FROM site_history sh
            JOIN sites s ON sh.site_id = s.id
            WHERE sh.user_id = %s
        """, (current_user.id,))
        sites_data = cur.fetchall()

        # Get all asset history
        cur.execute("""
            SELECT ah.asset_id, ah.amount, ah.currency, ah.recorded_at, a.name
            FROM asset_history ah
            JOIN assets a ON ah.asset_id = a.id
            WHERE ah.user_id = %s
        """, (current_user.id,))
        assets_data = cur.fetchall()

        all_data_points = []
        for row in sites_data:
            amount_usd = Decimal(str(row['amount'])) / currency_rates.get(row['currency'], Decimal('1.0'))
            all_data_points.append({
                'date': row['recorded_at'],
                'amount_usd': amount_usd,
                'name': row['name'],
                'type': 'site'
            })
        for row in assets_data:
            amount_usd = Decimal(str(row['amount'])) / currency_rates.get(row['currency'], Decimal('1.0'))
            all_data_points.append({
                'date': row['recorded_at'],
                'amount_usd': amount_usd,
                'name': row['name'],
                'type': 'asset'
            })

        # Sort all points by date
        all_points_sorted = sorted(all_data_points, key=lambda x: x['date'])

        if not all_points_sorted:
            return jsonify({'datasets': [{'label': 'Total Bankroll (USD)', 'data': [], 'fill': False, 'borderColor': 'rgb(75, 192, 192)', 'tension': 0.1}]})

        # Determine min and max dates
        min_day = all_points_sorted[0]['date'].date()
        max_day = all_points_sorted[-1]['date'].date()

        # Initialize charting data
        chart_data = []
        latest_values = {}
        current_total = Decimal('0')
        i = 0
        current_day = min_day

        while current_day <= max_day:
            # Process all updates for this day (update running total)
            while i < len(all_points_sorted) and all_points_sorted[i]['date'].date() == current_day:
                point = all_points_sorted[i]
                key = (point['name'], point['type'])
                new_value = point['amount_usd']
                old_value = latest_values.get(key, Decimal('0'))
                current_total += new_value - old_value
                latest_values[key] = new_value
                i += 1

            # Add one point for this day (using end-of-day total, or carried forward)
            chart_data.append({
                'x': current_day.isoformat(),
                'y': float(round(current_total, 2))  # Convert to float for JSON serialization
            })

            # Move to next day
            current_day += timedelta(days=1)

        datasets = [{
            'label': 'Total Bankroll (USD)',
            'data': chart_data,
            'fill': False,
            'borderColor': 'rgb(75, 192, 192)',
            'tension': 0.1
        }]

        cur.close()
        return jsonify({
            'datasets': datasets
        })
    except Exception as e:
        current_app.logger.error(f"Error in get_bankroll_data: {e}")
        return jsonify({'error': str(e)}), 500