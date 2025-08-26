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

@charts_bp.route("/poker_sites/line")
def poker_sites_line_chart_page():
    """Poker Sites Line Chart page."""
    return render_template("poker_sites_line_chart.html")

@charts_bp.route("/poker_sites/bar")
def poker_sites_bar_chart_page():
    """Poker Sites Bar Chart page."""
    return render_template("poker_sites_bar_chart.html")

@charts_bp.route("/poker_sites/pie")
def poker_sites_pie_chart_page():
    """Poker Sites Pie Chart page."""
    return render_template("poker_sites_pie_chart.html")

@charts_bp.route("/poker_sites/polar_area")
def poker_sites_polar_area_chart_page():
    """Poker Sites Polar Area Chart page."""
    return render_template("poker_sites_polar_area_chart.html")

@charts_bp.route("/poker_sites/radar")
def poker_sites_radar_chart_page():
    """Poker Sites Radar Chart page."""
    return render_template("poker_sites_radar_chart.html")

@charts_bp.route("/poker_sites/scatter")
def poker_sites_scatter_chart_page():
    """Poker Sites Scatter Chart page."""
    return render_template("poker_sites_scatter_chart.html")

@charts_bp.route("/assets/line")
def assets_line_chart_page():
    """Assets Line Chart page."""
    return render_template("assets_line_chart.html")

@charts_bp.route("/assets/bar")
def assets_bar_chart_page():
    """Assets Bar Chart page."""
    return render_template("assets_bar_chart.html")

@charts_bp.route("/assets/scatter")
def assets_scatter_chart_page():
    """Assets Scatter Chart page."""
    return render_template("assets_scatter_chart.html")

@charts_bp.route("/assets/pie")
def assets_pie_chart_page():
    """Assets Pie Chart page."""
    return render_template("assets_pie_chart.html")

@charts_bp.route("/assets/polar_area")
def assets_polar_area_chart_page():
    """Assets Polar Area Chart page."""
    return render_template("assets_polar_area_chart.html")

@charts_bp.route("/assets/radar")
def assets_radar_chart_page():
    """Assets Radar Chart page."""
    return render_template("assets_radar_chart.html")

@charts_bp.route("/bankroll/line")
def bankroll_line_chart_page():
    """Bankroll Line Chart page."""
    return render_template("bankroll_line_chart.html")

@charts_bp.route("/bankroll/bar")
def bankroll_bar_chart_page():
    """Bankroll Bar Chart page."""
    return render_template("bankroll_bar_chart.html")

@charts_bp.route("/bankroll/data")
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

@charts_bp.route("/poker_sites_historical_data")
@login_required
def get_poker_sites_historical_data():
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
            ORDER BY sh.recorded_at
        """, (current_user.id,))
        sites_data = cur.fetchall()

        if not sites_data:
            return jsonify({'labels': [], 'datasets': []})

        # Group data by site
        site_data_points = {}
        dates = set()
        for row in sites_data:
            site_name = row['name']
            date = row['recorded_at'].date()
            amount_usd = Decimal(str(row['amount'])) / currency_rates.get(row['currency'], Decimal('1.0'))
            if site_name not in site_data_points:
                site_data_points[site_name] = []
            site_data_points[site_name].append({
                'date': date,
                'amount_usd': amount_usd
            })
            dates.add(date)

        # Sort dates for labels
        labels = sorted([date.isoformat() for date in dates])

        # Create datasets for each site
        datasets = []
        colors = [
            'rgb(75, 192, 192)',  # Cyan
            'rgb(255, 99, 132)',   # Red
            'rgb(54, 162, 235)',   # Blue
            'rgb(255, 206, 86)',   # Yellow
            'rgb(153, 102, 255)',  # Purple
            'rgb(255, 159, 64)'    # Orange
        ]
        color_index = 0

        for site_name, points in site_data_points.items():
            # Sort points by date
            points_sorted = sorted(points, key=lambda x: x['date'])
            # Create data array aligned with labels
            data = []
            point_index = 0
            for date in sorted(dates):
                if point_index < len(points_sorted) and points_sorted[point_index]['date'] == date:
                    data.append(float(round(points_sorted[point_index]['amount_usd'], 2)))  # Convert to float for JSON
                    point_index += 1
                else:
                    # Carry forward the last known value or use 0 if no previous value
                    if point_index > 0:
                        data.append(float(round(points_sorted[point_index - 1]['amount_usd'], 2)))
                    else:
                        data.append(0.0)

            datasets.append({
                'label': site_name,
                'data': data,
                'fill': False,
                'borderColor': colors[color_index % len(colors)],
                'tension': 0.1
            })
            color_index += 1

        cur.close()
        return jsonify({
            'labels': labels,
            'datasets': datasets
        })
    except Exception as e:
        current_app.logger.error(f"Error in get_poker_sites_historical_data: {e}")
        return jsonify({'error': str(e)}), 500

@charts_bp.route("/assets_historical_data")
@login_required
def get_assets_historical_data():
    try:
        conn = get_db()
        cur = conn.cursor()

        cur.execute("SELECT name, rate FROM currency")
        currency_rates = {row['name']: Decimal(str(row['rate'])) for row in cur.fetchall()}

        cur.execute("""
            SELECT ah.asset_id, ah.amount, ah.currency, ah.recorded_at, a.name
            FROM asset_history ah
            JOIN assets a ON ah.asset_id = a.id
            WHERE ah.user_id = %s
            ORDER BY ah.recorded_at
        """, (current_user.id,))
        assets_data = cur.fetchall()

        if not assets_data:
            return jsonify({'labels': [], 'datasets': []})

        asset_data_points = {}
        dates = set()
        for row in assets_data:
            asset_name = row['name']
            date = row['recorded_at'].date()
            amount_usd = Decimal(str(row['amount'])) / currency_rates.get(row['currency'], Decimal('1.0'))
            if asset_name not in asset_data_points:
                asset_data_points[asset_name] = []
            asset_data_points[asset_name].append({
                'date': date,
                'amount_usd': amount_usd
            })
            dates.add(date)

        labels = sorted([date.isoformat() for date in dates])

        datasets = []
        colors = [
            'rgb(75, 192, 192)', 'rgb(255, 99, 132)', 'rgb(54, 162, 235)',
            'rgb(255, 206, 86)', 'rgb(153, 102, 255)', 'rgb(255, 159, 64)'
        ]
        color_index = 0

        for asset_name, points in asset_data_points.items():
            points_sorted = sorted(points, key=lambda x: x['date'])
            data = []
            point_index = 0
            for date in sorted(dates):
                if point_index < len(points_sorted) and points_sorted[point_index]['date'] == date:
                    data.append(float(round(points_sorted[point_index]['amount_usd'], 2)))
                    point_index += 1
                else:
                    if point_index > 0:
                        data.append(float(round(points_sorted[point_index - 1]['amount_usd'], 2)))
                    else:
                        data.append(0.0)

            datasets.append({
                'label': asset_name,
                'data': data,
                'fill': False,
                'borderColor': colors[color_index % len(colors)],
                'tension': 0.1
            })
            color_index += 1

        cur.close()
        return jsonify({
            'labels': labels,
            'datasets': datasets
        })
    except Exception as e:
        current_app.logger.error(f"Error in get_assets_historical_data: {e}")
        return jsonify({'error': str(e)}), 500

@charts_bp.route("/assets_pie_data")
@login_required
def get_assets_pie_data():
    try:
        conn = get_db()
        cur = conn.cursor()

        cur.execute("SELECT name, rate FROM currency")
        currency_rates = {row['name']: Decimal(str(row['rate'])) for row in cur.fetchall()}

        cur.execute("""
            SELECT ah.asset_id, ah.amount, ah.currency, ah.recorded_at, a.name
            FROM asset_history ah
            JOIN assets a ON ah.asset_id = a.id
            WHERE ah.user_id = %s
            ORDER BY ah.recorded_at DESC
        """, (current_user.id,))
        assets_data = cur.fetchall()

        latest_asset_values = {}
        for row in assets_data:
            asset_id = row['asset_id']
            if asset_id not in latest_asset_values:
                latest_asset_values[asset_id] = {
                    'name': row['name'],
                    'amount_usd': Decimal(str(row['amount'])) / currency_rates.get(row['currency'], Decimal('1.0'))
                }

        labels = [value['name'] for value in latest_asset_values.values()]
        data = [float(round(value['amount_usd'], 2)) for value in latest_asset_values.values()]

        cur.close()
        return jsonify({'labels': labels, 'datasets': [{'data': data}]})

    except Exception as e:
        current_app.logger.error(f"Error in get_assets_pie_data: {e}")
        return jsonify({'error': str(e)}), 500

@charts_bp.route("/profit_data")
@login_required
def get_profit_data():
    try:
        conn = get_db()
        cur = conn.cursor()

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

        # Get all deposits
        cur.execute("""
            SELECT amount, currency, date
            FROM deposits
            WHERE user_id = %s
        """, (current_user.id,))
        deposits_data = cur.fetchall()

        # Get all withdrawals
        cur.execute("""
            SELECT amount, currency, date
            FROM drawings
            WHERE user_id = %s
        """, (current_user.id,))
        withdrawals_data = cur.fetchall()

        all_financial_events = []

        # Add site history as bankroll changes
        for row in sites_data:
            amount_usd = Decimal(str(row['amount'])) / currency_rates.get(row['currency'], Decimal('1.0'))
            all_financial_events.append({
                'date': row['recorded_at'],
                'type': 'bankroll_change',
                'amount_usd': amount_usd
            })

        # Add asset history as bankroll changes
        for row in assets_data:
            amount_usd = Decimal(str(row['amount'])) / currency_rates.get(row['currency'], Decimal('1.0'))
            all_financial_events.append({
                'date': row['recorded_at'],
                'type': 'bankroll_change',
                'amount_usd': amount_usd
            })

        # Add deposits
        for row in deposits_data:
            amount_usd = Decimal(str(row['amount'])) / currency_rates.get(row['currency'], Decimal('1.0'))
            all_financial_events.append({
                'date': row['date'],
                'type': 'deposit',
                'amount_usd': amount_usd
            })

        # Add withdrawals
        for row in withdrawals_data:
            amount_usd = Decimal(str(row['amount'])) / currency_rates.get(row['currency'], Decimal('1.0'))
            all_financial_events.append({
                'date': row['date'],
                'type': 'withdrawal',
                'amount_usd': amount_usd
            })

        # Sort all events by date
        all_financial_events_sorted = sorted(all_financial_events, key=lambda x: x['date'])

        if not all_financial_events_sorted:
            return jsonify({'labels': [], 'datasets': []})

        profit_data = []
        current_bankroll = Decimal('0')
        total_deposits = Decimal('0')
        total_withdrawals = Decimal('0')
        
        # Initialize latest_bankroll_values to track the latest value for each site/asset
        latest_bankroll_values = {}

        # Determine min and max dates
        min_day = all_financial_events_sorted[0]['date'].date()
        max_day = all_financial_events_sorted[-1]['date'].date()

        current_day = min_day
        event_index = 0

        while current_day <= max_day:
            # Process all events for the current day
            while (event_index < len(all_financial_events_sorted) and
                   all_financial_events_sorted[event_index]['date'].date() == current_day):
                
                event = all_financial_events_sorted[event_index]
                
                if event['type'] == 'deposit':
                    total_deposits += event['amount_usd']
                elif event['type'] == 'withdrawal':
                    total_withdrawals += event['amount_usd']
                elif event['type'] == 'bankroll_change':
                    # For bankroll changes, we need to update the latest value for that specific site/asset
                    # This part is tricky as the current structure doesn't differentiate between sites/assets
                    # For simplicity, let's assume 'bankroll_change' events represent the total bankroll at that point
                    # This might need refinement if the user wants profit per site/asset
                    current_bankroll = event['amount_usd'] # This assumes the event amount is the total bankroll
                    
                event_index += 1

            # Calculate profit for the current day
            # Profit = (Current Bankroll + Total Withdrawals) - Total Deposits
            profit_for_day = (current_bankroll + total_withdrawals) - total_deposits
            
            profit_data.append({
                'x': current_day.isoformat(),
                'y': float(round(profit_for_day, 2))
            })
            
            current_day += timedelta(days=1)

        datasets = [{
            'label': 'Profit (USD)',
            'data': profit_data,
            'fill': False,
            'borderColor': 'rgb(0, 128, 0)', # Green color for profit
            'tension': 0.1
        }]

        cur.close()
        return jsonify({
            'datasets': datasets
        })

    except Exception as e:
        current_app.logger.error(f"Error in get_profit_data: {e}")
        return jsonify({'error': str(e)}), 500

@charts_bp.route("/withdrawals_data")
@login_required
def get_withdrawals_data():
    try:
        conn = get_db()
        cur = conn.cursor()

        cur.execute("SELECT name, rate FROM currency")
        currency_rates = {row['name']: Decimal(str(row['rate'])) for row in cur.fetchall()}

        cur.execute("""
            SELECT amount, currency, date
            FROM drawings
            WHERE user_id = %s
            ORDER BY date
        """, (current_user.id,))
        withdrawals_raw = cur.fetchall()

        if not withdrawals_raw:
            return jsonify({'labels': [], 'datasets': []})

        withdrawals_by_date = {}
        dates = set()
        for row in withdrawals_raw:
            date = row['date'].date()
            amount_usd = Decimal(str(row['amount'])) / currency_rates.get(row['currency'], Decimal('1.0'))
            
            if date not in withdrawals_by_date:
                withdrawals_by_date[date] = Decimal('0')
            withdrawals_by_date[date] += amount_usd
            dates.add(date)

        labels = sorted([date.isoformat() for date in dates])
        data = [float(round(withdrawals_by_date.get(datetime.fromisoformat(label).date(), Decimal('0')), 2)) for label in labels]

        datasets = [{
            'label': 'Total Withdrawals (USD)',
            'data': data,
            'fill': False,
            'borderColor': 'rgb(255, 99, 132)', # Red color for withdrawals
            'tension': 0.1
        }]

        cur.close()
        return jsonify({
            'labels': labels,
            'datasets': datasets
        })
    except Exception as e:
        current_app.logger.error(f"Error in get_withdrawals_data: {e}")
        return jsonify({'error': str(e)}), 500

@charts_bp.route("/deposits_data")
@login_required
def get_deposits_data():
    try:
        conn = get_db()
        cur = conn.cursor()

        cur.execute("SELECT name, rate FROM currency")
        currency_rates = {row['name']: Decimal(str(row['rate'])) for row in cur.fetchall()}

        cur.execute("""
            SELECT amount, currency, date
            FROM deposits
            WHERE user_id = %s
            ORDER BY date
        """, (current_user.id,))
        deposits_raw = cur.fetchall()

        if not deposits_raw:
            return jsonify({'labels': [], 'datasets': []})

        deposits_by_date = {}
        dates = set()
        for row in deposits_raw:
            date = row['date'].date()
            amount_usd = Decimal(str(row['amount'])) / currency_rates.get(row['currency'], Decimal('1.0'))
            
            if date not in deposits_by_date:
                deposits_by_date[date] = Decimal('0')
            deposits_by_date[date] += amount_usd
            dates.add(date)

        labels = sorted([date.isoformat() for date in dates])
        data = [float(round(deposits_by_date.get(datetime.fromisoformat(label).date(), Decimal('0')), 2)) for label in labels]

        datasets = [{
            'label': 'Total Deposits (USD)',
            'data': data,
            'fill': False,
            'borderColor': 'rgb(75, 192, 192)', # Green color for deposits
            'tension': 0.1
        }]

        cur.close()
        return jsonify({
            'labels': labels,
            'datasets': datasets
        })
    except Exception as e:
        current_app.logger.error(f"Error in get_deposits_data: {e}")
        return jsonify({'error': str(e)}), 500

@charts_bp.route("/deposits/line")
def deposits_line_chart_page():
    """Deposits Line Chart page."""
    return render_template("deposits_line_chart.html")

@charts_bp.route("/deposits/bar")
def deposits_bar_chart_page():
    """Deposits Bar Chart page."""
    return render_template("deposits_bar_chart.html")

@charts_bp.route("/withdrawals/line")
def withdrawals_line_chart_page():
    """Withdrawals Line Chart page."""
    return render_template("withdrawals_line_chart.html")

@charts_bp.route("/withdrawals/bar")
def withdrawals_bar_chart_page():
    """Withdrawals Bar Chart page."""
    return render_template("withdrawals_bar_chart.html")

@charts_bp.route("/profit/line")
def profit_line_chart_page():
    """Profit Line Chart page."""
    return render_template("profit_line_chart.html")

@charts_bp.route("/profit/bar")
def profit_bar_chart_page():
    """Profit Bar Chart page."""
    return render_template("profit_bar_chart.html")

@charts_bp.route("/poker_sites_pie_data")
@login_required
def get_poker_sites_pie_data():
    try:
        conn = get_db()
        cur = conn.cursor()

        cur.execute("SELECT name, rate FROM currency")
        currency_rates = {row['name']: Decimal(str(row['rate'])) for row in cur.fetchall()}

        cur.execute("""
            SELECT sh.site_id, sh.amount, sh.currency, sh.recorded_at, s.name
            FROM site_history sh
            JOIN sites s ON sh.site_id = s.id
            WHERE sh.user_id = %s
            ORDER BY sh.recorded_at DESC
        """, (current_user.id,))
        sites_data = cur.fetchall()

        latest_site_values = {}
        for row in sites_data:
            site_id = row['site_id']
            if site_id not in latest_site_values:
                latest_site_values[site_id] = {
                    'name': row['name'],
                    'amount_usd': Decimal(str(row['amount'])) / currency_rates.get(row['currency'], Decimal('1.0'))
                }

        labels = [value['name'] for value in latest_site_values.values()]
        data = [float(round(value['amount_usd'], 2)) for value in latest_site_values.values()]

        cur.close()
        return jsonify({'labels': labels, 'datasets': [{'data': data}]})

    except Exception as e:
        current_app.logger.error(f"Error in get_poker_sites_pie_data: {e}")
        return jsonify({'error': str(e)}), 500