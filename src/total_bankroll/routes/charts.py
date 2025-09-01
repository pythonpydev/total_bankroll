from flask import Blueprint, render_template, jsonify, current_app, abort
from flask_security import current_user, login_required
from ..extensions import db
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy import text

charts_bp = Blueprint("charts", __name__)

@charts_bp.route("/charts")
@login_required
def charts_page():
    """Charts page."""
    return render_template("charts.html")

@charts_bp.route("/<string:entity>/<string:chart_type>")
@login_required
def generic_chart_page(entity, chart_type):
    """Renders a generic chart page for a given entity and chart type."""
    allowed_entities = ["poker_sites", "assets", "bankroll", "profit", "withdrawals", "deposits"]
    allowed_chart_types = ["line", "bar", "pie", "polar_area", "radar", "scatter"]

    if entity not in allowed_entities or chart_type not in allowed_chart_types:
        abort(404)

    template_name = f"{entity}_{chart_type}_chart.html"
    try:
        return render_template(template_name)
    except Exception:
        # If a specific template doesn't exist (e.g., profit_pie_chart.html), abort.
        abort(404)

@charts_bp.route("/bankroll/data")
@login_required
def get_bankroll_data():
    try:
        with db.session.connection() as conn:
            # Get currency rates
            result = conn.execute(text("SELECT code, rate FROM currency"))
            currency_rates = {row['code']: Decimal(str(row['rate'])) for row in result.mappings()}

            # Get all site history
            sites_sql = text("""
                SELECT sh.site_id, sh.amount, sh.currency, sh.recorded_at, s.name
                FROM site_history sh
                JOIN sites s ON sh.site_id = s.id
                WHERE sh.user_id = :user_id
            """)
            sites_data = conn.execute(sites_sql, {'user_id': current_user.id}).mappings().all()

            # Get all asset history
            assets_sql = text("""
                SELECT ah.asset_id, ah.amount, ah.currency, ah.recorded_at, a.name
                FROM asset_history ah
                JOIN assets a ON ah.asset_id = a.id
                WHERE ah.user_id = :user_id
            """)
            assets_data = conn.execute(assets_sql, {'user_id': current_user.id}).mappings().all()

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
        with db.session.connection() as conn:
            # Get currency rates
            result = conn.execute(text("SELECT code, rate FROM currency"))
            currency_rates = {row['code']: Decimal(str(row['rate'])) for row in result.mappings()}

            # Get all site history
            sql = text("""
                SELECT sh.site_id, sh.amount, sh.currency, sh.recorded_at, s.name
                FROM site_history sh
                JOIN sites s ON sh.site_id = s.id
                WHERE sh.user_id = :user_id
                ORDER BY sh.recorded_at
            """)
            sites_data = conn.execute(sql, {'user_id': current_user.id}).mappings().all()

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
        sorted_dates = sorted(list(dates))
        labels = [d.isoformat() for d in sorted_dates]
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
            for date in sorted_dates:
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

        return jsonify({
            'labels': labels,
            'datasets': datasets,
            'min_date': labels[0] if labels else None,
            'max_date': labels[-1] if labels else None
        })
    except Exception as e:
        current_app.logger.error(f"Error in get_poker_sites_historical_data: {e}")
        return jsonify({'error': str(e)}), 500

@charts_bp.route("/assets_historical_data")
@login_required
def get_assets_historical_data():
    try:
        with db.session.connection() as conn:
            currency_result = conn.execute(text("SELECT code, rate FROM currency"))
            currency_rates = {row['code']: Decimal(str(row['rate'])) for row in currency_result.mappings()}

            sql = text("""
                SELECT ah.asset_id, ah.amount, ah.currency, ah.recorded_at, a.name
                FROM asset_history ah
                JOIN assets a ON ah.asset_id = a.id
                WHERE ah.user_id = :user_id
                ORDER BY ah.recorded_at
            """)
            assets_data = conn.execute(sql, {'user_id': current_user.id}).mappings().all()

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

        sorted_dates = sorted(list(dates))
        labels = [d.isoformat() for d in sorted_dates]
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
            for date in sorted_dates:
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

        return jsonify({
            'labels': labels,
            'datasets': datasets,
            'min_date': labels[0] if labels else None,
            'max_date': labels[-1] if labels else None
        })
    except Exception as e:
        current_app.logger.error(f"Error in get_assets_historical_data: {e}")
        return jsonify({'error': str(e)}), 500

@charts_bp.route("/assets_pie_data")
@login_required
def get_assets_pie_data():
    try:
        with db.session.connection() as conn:
            currency_result = conn.execute(text("SELECT code, rate FROM currency"))
            currency_rates = {row['code']: Decimal(str(row['rate'])) for row in currency_result.mappings()}

            sql = text("""
                SELECT ah.asset_id, ah.amount, ah.currency, ah.recorded_at, a.name
                FROM asset_history ah
                JOIN assets a ON ah.asset_id = a.id
                WHERE ah.user_id = :user_id
                ORDER BY ah.recorded_at DESC
            """)
            assets_data = conn.execute(sql, {'user_id': current_user.id}).mappings().all()

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

        return jsonify({'labels': labels, 'datasets': [{'data': data}]})

    except Exception as e:
        current_app.logger.error(f"Error in get_assets_pie_data: {e}")
        return jsonify({'error': str(e)}), 500

@charts_bp.route("/profit_data")
@login_required
def get_profit_data():
    try:
        with db.session.connection() as conn:
            currency_result = conn.execute(text("SELECT code, rate FROM currency"))
            currency_rates = {row['code']: Decimal(str(row['rate'])) for row in currency_result.mappings()}

            # Get all site history
            sites_sql = text("""
                SELECT sh.site_id, sh.amount, sh.currency, sh.recorded_at, s.name
                FROM site_history sh
                JOIN sites s ON sh.site_id = s.id
                WHERE sh.user_id = :user_id
            """)
            sites_data = conn.execute(sites_sql, {'user_id': current_user.id}).mappings().all()

            # Get all asset history
            assets_sql = text("""
                SELECT ah.asset_id, ah.amount, ah.currency, ah.recorded_at, a.name
                FROM asset_history ah
                JOIN assets a ON ah.asset_id = a.id
                WHERE ah.user_id = :user_id
            """)
            assets_data = conn.execute(assets_sql, {'user_id': current_user.id}).mappings().all()

            # Get all deposits
            deposits_sql = text("""
                SELECT amount, currency, date
                FROM deposits
                WHERE user_id = :user_id
            """)
            deposits_data = conn.execute(deposits_sql, {'user_id': current_user.id}).mappings().all()

            # Get all withdrawals
            withdrawals_sql = text("""
                SELECT amount, currency, date
                FROM drawings
                WHERE user_id = :user_id
            """)
            withdrawals_data = conn.execute(withdrawals_sql, {'user_id': current_user.id}).mappings().all()

        all_financial_events = []

        # Add site history
        for row in sites_data:
            amount_usd = Decimal(str(row['amount'])) / currency_rates.get(row['currency'], Decimal('1.0'))
            all_financial_events.append({
                'date': row['recorded_at'],
                'type': 'bankroll_update',
                'name': row['name'],
                'entity_type': 'site',
                'amount_usd': amount_usd
            })

        # Add asset history as bankroll changes
        for row in assets_data:
            amount_usd = Decimal(str(row['amount'])) / currency_rates.get(row['currency'], Decimal('1.0'))
            all_financial_events.append({
                'date': row['recorded_at'],
                'type': 'bankroll_update',
                'name': row['name'],
                'entity_type': 'asset',
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
        latest_bankroll_values = {} # To track latest value for each site/asset

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
                elif event['type'] == 'bankroll_update':
                    key = (event['name'], event['entity_type'])
                    new_value = event['amount_usd']
                    old_value = latest_bankroll_values.get(key, Decimal('0'))
                    current_bankroll += new_value - old_value
                    latest_bankroll_values[key] = new_value
                    
                event_index += 1

            # Calculate profit for the current day
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
        with db.session.connection() as conn:
            currency_result = conn.execute(text("SELECT code, rate FROM currency"))
            currency_rates = {row['code']: Decimal(str(row['rate'])) for row in currency_result.mappings()}

            sql = text("""
                SELECT amount, currency, date
                FROM drawings
                WHERE user_id = :user_id
                ORDER BY date
            """)
            withdrawals_raw = conn.execute(sql, {'user_id': current_user.id}).mappings().all()

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
        with db.session.connection() as conn:
            currency_result = conn.execute(text("SELECT code, rate FROM currency"))
            currency_rates = {row['code']: Decimal(str(row['rate'])) for row in currency_result.mappings()}

            sql = text("""
                SELECT amount, currency, date
                FROM deposits
                WHERE user_id = :user_id
                ORDER BY date
            """)
            deposits_raw = conn.execute(sql, {'user_id': current_user.id}).mappings().all()

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

        return jsonify({
            'labels': labels,
            'datasets': datasets
        })
    except Exception as e:
        current_app.logger.error(f"Error in get_deposits_data: {e}")
        return jsonify({'error': str(e)}), 500

@charts_bp.route("/poker_sites_pie_data")
@login_required
def get_poker_sites_pie_data():
    try:
        with db.session.connection() as conn:
            currency_result = conn.execute(text("SELECT code, rate FROM currency"))
            currency_rates = {row['code']: Decimal(str(row['rate'])) for row in currency_result.mappings()}

            sql = text("""
                SELECT sh.site_id, sh.amount, sh.currency, sh.recorded_at, s.name
                FROM site_history sh
                JOIN sites s ON sh.site_id = s.id
                WHERE sh.user_id = :user_id
                ORDER BY sh.recorded_at DESC
            """)
            sites_data = conn.execute(sql, {'user_id': current_user.id}).mappings().all()

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

        return jsonify({'labels': labels, 'datasets': [{'data': data}]})

    except Exception as e:
        current_app.logger.error(f"Error in get_poker_sites_pie_data: {e}")
        return jsonify({'error': str(e)}), 500