from flask import Blueprint, render_template, jsonify, current_app
from flask_security import current_user, login_required
from ..db import get_db
from datetime import datetime

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

@charts_bp.route("/charts/deposits/line")
def deposits_line_chart_page():
    """Deposits Line Chart page."""
    return render_template("deposits_line_chart.html")

@charts_bp.route("/charts/deposits/bar")
def deposits_bar_chart_page():
    """Deposits Bar Chart page."""
    return render_template("deposits_bar_chart.html")

@charts_bp.route("/charts/poker_sites_data")
def get_poker_sites_data():
    try:
        conn = get_db()
        cur = conn.cursor()

        # Get all unique poker site names and their IDs
        cur.execute("SELECT id, name FROM sites WHERE user_id = %s ORDER BY name", (current_user.id,))
        sites = cur.fetchall()

        # Get currency exchange rates
        cur.execute("SELECT name, rate FROM currency")
        currency_rates = {row['name']: row['rate'] for row in cur.fetchall()}

        cur.close()

        labels = []
        data = []

        for site in sites:
            # Get the latest amount for each site from site_history
            cur = conn.cursor() # Re-open cursor for inner query
            cur.execute("SELECT amount, currency FROM site_history WHERE site_id = %s AND user_id = %s ORDER BY recorded_at DESC LIMIT 1", (site['id'], current_user.id))
            latest_record = cur.fetchone()
            cur.close()

            if latest_record:
                amount_usd = float(latest_record['amount']) / float(currency_rates.get(latest_record['currency'], 1.0))
                labels.append(site['name'])
                data.append(amount_usd)

        # Prepare data for Chart.js
        datasets = [{
            'label': 'Latest Amount (USD)',
            'data': data,
            'backgroundColor': [
                'rgba(255, 99, 132, 0.6)', # Red
                'rgba(54, 162, 235, 0.6)', # Blue
                'rgba(255, 206, 86, 0.6)', # Yellow
                'rgba(75, 192, 192, 0.6)', # Green
                'rgba(153, 102, 255, 0.6)',# Purple
                'rgba(255, 159, 64, 0.6)'  # Orange
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

        # Get all unique poker site names and their IDs
        cur.execute("SELECT id, name FROM sites WHERE user_id = %s ORDER BY name", (current_user.id,))
        sites = cur.fetchall()

        # Get currency exchange rates
        cur.execute("SELECT name, rate FROM currency")
        currency_rates = {row['name']: row['rate'] for row in cur.fetchall()}

        cur.close()

        processed_data = {}
        min_date = None
        max_date = None

        for site in sites:
            site_name = site['name']
            site_id = site['id']

            # Get all historical data for this site
            cur = conn.cursor() # Re-open cursor for inner query
            cur.execute("SELECT amount, currency, recorded_at FROM site_history WHERE site_id = %s AND user_id = %s ORDER BY recorded_at", (site_id, current_user.id))
            raw_data = cur.fetchall()
            cur.close()

            daily_data = {}
            for row in raw_data:
                date_obj = row['recorded_at']
                date_str = date_obj.strftime("%Y-%m-%d")
                if min_date is None or date_obj < min_date:
                    min_date = date_obj
                if max_date is None or date_obj > max_date:
                    max_date = date_obj

                amount_usd = float(row['amount']) / float(currency_rates.get(row['currency'], 1.0))
                daily_data[date_str] = amount_usd # Only keep the last update for the day

            if site_name not in processed_data:
                processed_data[site_name] = []
            
            # Sort items by date to ensure chronological order before appending
            sorted_dates = sorted(daily_data.items())
            for date_str, amount_usd in sorted_dates:
                processed_data[site_name].append({'x': date_str, 'y': amount_usd})

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

        if min_date and max_date:
            min_date_str = min_date.strftime("%Y-%m-%d")
            max_date_str = max_date.strftime("%Y-%m-%d")

            for i, site in enumerate(sites):
                site_name = site['name']
                site_data = processed_data.get(site_name, [])
                if site_data:
                    # Sort by date to ensure chronological order
                    site_data.sort(key=lambda item: item['x'])
                    # Insert y=0 at min_date if needed
                    if site_data[0]['x'] > min_date_str:
                        site_data.insert(0, {'x': min_date_str, 'y': 0})
                    # Extend last value to max_date if needed
                    if site_data[-1]['x'] < max_date_str:
                        site_data.append({'x': max_date_str, 'y': site_data[-1]['y']})
                    # Re-sort after adding min_date and max_date to maintain order
                    site_data.sort(key=lambda item: item['x'])

                datasets.append({
                    'label': site_name,
                    'data': site_data,
                    'borderColor': border_colors[i % len(border_colors)],
                    'fill': False
                })

        return jsonify({
            'labels': [site['name'] for site in sites], # Labels are not directly used for scatter, but can be for legend
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

        # Get all unique asset names and their IDs
        cur.execute("SELECT id, name FROM assets WHERE user_id = %s ORDER BY name", (current_user.id,))
        assets = cur.fetchall()

        # Get currency exchange rates
        cur.execute("SELECT name, rate FROM currency")
        currency_rates = {row['name']: row['rate'] for row in cur.fetchall()}

        cur.close()

        labels = []
        data = []

        for asset in assets:
            # Get the latest amount for each asset from asset_history
            cur = conn.cursor() # Re-open cursor for inner query
            cur.execute("SELECT amount, currency FROM asset_history WHERE asset_id = %s AND user_id = %s ORDER BY recorded_at DESC LIMIT 1", (asset['id'], current_user.id))
            latest_record = cur.fetchone()
            cur.close()

            if latest_record:
                amount_usd = float(latest_record['amount']) / float(currency_rates.get(latest_record['currency'], 1.0))
                labels.append(asset['name'])
                data.append(amount_usd)

        # Prepare data for Chart.js
        datasets = [{
            'label': 'Latest Amount (USD)',
            'data': data,
            'backgroundColor': [
                'rgba(255, 99, 132, 0.6)', # Red
                'rgba(54, 162, 235, 0.6)', # Blue
                'rgba(255, 206, 86, 0.6)', # Yellow
                'rgba(75, 192, 192, 0.6)', # Green
                'rgba(153, 102, 255, 0.6)',# Purple
                'rgba(255, 159, 64, 0.6)'  # Orange
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
        current_app.logger.error(f"Error in get_assets_data: {e}")
        return jsonify({'error': str(e)}), 500

@charts_bp.route("/charts/assets_pie_chart_data")
def get_assets_pie_chart_data():
    try:
        conn = get_db()
        cur = conn.cursor()

        # Get all unique asset names and their IDs for the current user
        cur.execute("SELECT id, name FROM assets WHERE user_id = %s ORDER BY name", (current_user.id,))
        assets = cur.fetchall()

        # Get currency exchange rates
        cur.execute("SELECT name, rate FROM currency")
        currency_rates = {row['name']: row['rate'] for row in cur.fetchall()}

        cur.close()

        labels = []
        data = []

        for asset in assets:
            # Get the latest amount for each asset from asset_history
            cur = conn.cursor() # Re-open cursor for inner query
            cur.execute("SELECT amount, currency FROM asset_history WHERE asset_id = %s AND user_id = %s ORDER BY recorded_at DESC LIMIT 1", (asset['id'], current_user.id))
            latest_record = cur.fetchone()
            cur.close()

            if latest_record:
                amount_usd = float(latest_record['amount']) / float(currency_rates.get(latest_record['currency'], 1.0))
                labels.append(asset['name'])
                data.append(amount_usd)

        # Prepare data for Chart.js
        datasets = [{
            'label': 'Latest Amount (USD)',
            'data': data,
            'backgroundColor': [
                'rgba(255, 99, 132, 0.6)', # Red
                'rgba(54, 162, 235, 0.6)', # Blue
                'rgba(255, 206, 86, 0.6)', # Yellow
                'rgba(75, 192, 192, 0.6)', # Green
                'rgba(153, 102, 255, 0.6)',# Purple
                'rgba(255, 159, 64, 0.6)'  # Orange
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
        current_app.logger.error(f"Error in get_assets_pie_chart_data: {e}")
        return jsonify({'error': str(e)}), 500

@charts_bp.route("/charts/deposits_data")
def get_deposits_data():
    try:
        conn = get_db()
        cur = conn.cursor()  # make sure this returns dict-like rows; otherwise adjust access below

        cur.execute("""
            SELECT
                d.date AS ts,
                SUM(d.amount / c.rate)
                  OVER (ORDER BY d.date, d.id) AS cumulative_usd
            FROM deposits d
            JOIN currency c ON d.currency = c.name
            WHERE d.user_id = %s
            ORDER BY d.date, d.id
        """, (current_user.id,))
        raw = cur.fetchall()
        cur.close()

        # If your cursor isn't dict-like, replace row['ts'] with row[0] etc.
        labels = [row['ts'].strftime("%Y-%m-%d %H:%M") for row in raw]
        data = [float(row['cumulative_usd']) for row in raw]

        datasets = [{
            'label': 'Cumulative Deposits (USD)',
            'data': data,
            'fill': False,
            'borderColor': 'rgb(54, 162, 235)',
            'tension': 0.1
        }]

        return jsonify({'labels': labels, 'datasets': datasets})
    except Exception as e:
        current_app.logger.error(f"Error in get_deposits_data: {e}")
        return jsonify({'error': str(e)}), 500

@charts_bp.route("/charts/withdrawals_data")
def get_withdrawals_data():
    try:
        conn = get_db()
        cur = conn.cursor()  # make sure this returns dict-like rows; otherwise adjust access below

        cur.execute("""
            SELECT
                d.date AS ts,
                SUM(d.amount / c.rate)
                  OVER (ORDER BY d.date, d.id) AS cumulative_usd
            FROM drawings d
            JOIN currency c ON d.currency = c.name
            WHERE d.user_id = %s
            ORDER BY d.date, d.id
        """, (current_user.id,))
        raw = cur.fetchall()
        cur.close()

        # If your cursor isn't dict-like, replace row['ts'] with row[0] etc.
        labels = [row['ts'].strftime("%Y-%m-%d %H:%M") for row in raw]
        data = [float(row['cumulative_usd']) for row in raw]

        datasets = [{
            'label': 'Cumulative Withdrawals (USD)',
            'data': data,
            'fill': False,
            'borderColor': 'rgb(54, 162, 235)',
            'tension': 0.1
        }]

        return jsonify({'labels': labels, 'datasets': datasets})
    except Exception as e:
        current_app.logger.error(f"Error in get_withdrawals_data: {e}")
        return jsonify({'error': str(e)}), 500



@charts_bp.route("/charts/profit_data")
def get_profit_data():
    """Returns data for the profit line chart, aggregated to one point per day."""
    try:
        conn = get_db()
        cur = conn.cursor()

        # Get currency exchange rates
        cur.execute("SELECT name, rate FROM currency")
        currency_rates = {row['name']: row['rate'] for row in cur.fetchall()}

        # Get historical data for sites
        cur.execute("SELECT sh.recorded_at, s.name, sh.amount, sh.currency FROM site_history sh JOIN sites s ON sh.site_id = s.id WHERE sh.user_id = %s ORDER BY sh.recorded_at", (current_user.id,))
        sites_data = cur.fetchall()

        # Get historical data for assets
        cur.execute("SELECT ah.recorded_at, a.name, ah.amount, ah.currency FROM asset_history ah JOIN assets a ON ah.asset_id = a.id WHERE ah.user_id = %s ORDER BY ah.recorded_at", (current_user.id,))
        assets_data = cur.fetchall()

        # Get historical data for deposits
        cur.execute("SELECT date, amount, currency FROM deposits WHERE user_id = %s ORDER BY date", (current_user.id,))
        deposits_data = cur.fetchall()

        # Get historical data for withdrawals
        cur.execute("SELECT date, amount, currency FROM drawings WHERE user_id = %s ORDER BY date", (current_user.id,))
        withdrawals_data = cur.fetchall()

        cur.close()

        all_data_points = []
        # Add bankroll components (sites and assets)
        for row in sites_data:
            amount_usd = float(row['amount']) / float(currency_rates.get(row['currency'], 1.0))
            all_data_points.append({'date': row['recorded_at'], 'amount_usd': amount_usd, 'name': row['name'], 'type': 'site'})
        for row in assets_data:
            amount_usd = float(row['amount']) / float(currency_rates.get(row['currency'], 1.0))
            all_data_points.append({'date': row['recorded_at'], 'amount_usd': amount_usd, 'name': row['name'], 'type': 'asset'})
        
        # Add deposits and withdrawals as events that change the profit calculation
        for row in deposits_data:
            amount_usd = float(row['amount']) / float(currency_rates.get(row['currency'], 1.0))
            all_data_points.append({'date': row['date'], 'amount_usd': amount_usd, 'type': 'deposit'})
        for row in withdrawals_data:
            amount_usd = float(row['amount']) / float(currency_rates.get(row['currency'], 1.0))
            all_data_points.append({'date': row['date'], 'amount_usd': amount_usd, 'type': 'withdrawal'})

        # Sort all points by date
        all_points_sorted = sorted(all_data_points, key=lambda x: x['date'])

        if not all_points_sorted:
            return jsonify({'datasets': [{'label': 'Total Profit (USD)', 'data': [], 'fill': False, 'borderColor': 'rgb(255, 99, 132)', 'tension': 0.1}]})

        min_day = all_points_sorted[0]['date'].date()
        max_day = all_points_sorted[-1]['date'].date()

        chart_data = []
        latest_values = {}
        current_bankroll = 0.0
        total_deposits = 0.0
        total_withdrawals = 0.0
        
        i = 0
        current_day = min_day
        from datetime import timedelta

        while current_day <= max_day:
            
            while i < len(all_points_sorted) and all_points_sorted[i]['date'].date() == current_day:
                point = all_points_sorted[i]
                
                if point['type'] in ['site', 'asset']:
                    key = (point['name'], point['type'])
                    new_value = point['amount_usd']
                    old_value = latest_values.get(key, 0.0)
                    current_bankroll += new_value - old_value
                    latest_values[key] = new_value
                elif point['type'] == 'deposit':
                    total_deposits += point['amount_usd']
                elif point['type'] == 'withdrawal':
                    total_withdrawals += point['amount_usd']
                
                i += 1
            
            profit = current_bankroll - total_deposits + total_withdrawals
            
            chart_data.append({
                'x': current_day.isoformat(),
                'y': round(profit, 2)
            })
            
            current_day += timedelta(days=1)

        datasets = [{
            'label': 'Total Profit (USD)',
            'data': chart_data,
            'fill': False,
            'borderColor': 'rgb(255, 99, 132)',
            'tension': 0.1
        }]

        return jsonify({'datasets': datasets})

    except Exception as e:
        current_app.logger.error(f"Error in get_profit_data: {e}")
        return jsonify({'error': str(e)}), 500

@charts_bp.route("/charts/bankroll_data")
def get_bankroll_data():
    """Returns data for the bankroll line chart, aggregated to one point per day."""
    try:
        conn = get_db()
        cur = conn.cursor()

        # Get currency exchange rates
        cur.execute("SELECT name, rate FROM currency")
        currency_rates = {row['name']: row['rate'] for row in cur.fetchall()}

        # Get historical data for sites (include name)
        cur.execute("SELECT sh.recorded_at, s.name, sh.amount, sh.currency FROM site_history sh JOIN sites s ON sh.site_id = s.id WHERE sh.user_id = %s ORDER BY sh.recorded_at", (current_user.id,))
        sites_data = cur.fetchall()

        # Get historical data for assets (include name)
        cur.execute("SELECT ah.recorded_at, a.name, ah.amount, ah.currency FROM asset_history ah JOIN assets a ON ah.asset_id = a.id WHERE ah.user_id = %s ORDER BY ah.recorded_at", (current_user.id,))
        assets_data = cur.fetchall()

        cur.close()

        # Combine and sort all data points by date
        all_data_points = []
        for row in sites_data:
            amount_usd = float(row['amount']) / float(currency_rates.get(row['currency'], 1.0))
            all_data_points.append({
                'date': row['recorded_at'],
                'amount_usd': amount_usd,
                'name': row['name'],
                'type': 'site'
            })
        for row in assets_data:
            amount_usd = float(row['amount']) / float(currency_rates.get(row['currency'], 1.0))
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
        current_total = 0.0
        i = 0
        current_day = min_day

        from datetime import timedelta  # Ensure this import is at the top of the file if not already

        while current_day <= max_day:
            # Process all updates for this day (update running total)
            while i < len(all_points_sorted) and all_points_sorted[i]['date'].date() == current_day:
                point = all_points_sorted[i]
                key = (point['name'], point['type'])
                new_value = point['amount_usd']
                old_value = latest_values.get(key, 0.0)
                current_total += new_value - old_value
                latest_values[key] = new_value
                i += 1

            # Add one point for this day (using end-of-day total, or carried forward)
            chart_data.append({
                'x': current_day.isoformat(),  # Date string without time (e.g., '2025-08-18')
                'y': round(current_total, 2)   # Rounded for display; adjust as needed
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

        return jsonify({
            'datasets': datasets
        })
    except Exception as e:
        current_app.logger.error(f"Error in get_bankroll_data: {e}")
        return jsonify({'error': str(e)}), 500