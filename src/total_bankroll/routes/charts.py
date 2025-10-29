from flask import Blueprint, render_template, jsonify, current_app, abort
from flask_security import current_user, login_required
from datetime import datetime, timedelta
from decimal import Decimal
from ..models import db, Currency, SiteHistory, Sites, AssetHistory, Assets, Deposits, Drawings

charts_bp = Blueprint("charts", __name__)

@charts_bp.route("/charts")
@login_required
def charts_page():
    """Charts page."""
    return render_template("charts/charts.html")

@charts_bp.route("/<string:entity>/<string:chart_type>")
@login_required
def generic_chart_page(entity, chart_type):
    """Renders a generic chart page for a given entity and chart type."""
    allowed_entities = ["poker_sites", "assets", "bankroll", "profit", "withdrawals", "deposits"]
    allowed_chart_types = ["line", "bar", "pie", "polar_area", "radar", "scatter"]

    if entity not in allowed_entities or chart_type not in allowed_chart_types:
        abort(404)

    template_name = f"charts/{entity}_{chart_type}_chart.html"
    try:
        return render_template(template_name)
    except Exception:
        # If a specific template doesn't exist (e.g., profit_pie_chart.html), abort.
        abort(404)

@charts_bp.route("/bankroll/data")
@login_required
def get_bankroll_data():
    try:
        # Get currency rates
        currency_rates_query = db.session.query(Currency.code, Currency.rate).all()
        currency_rates = {row.code: Decimal(str(row.rate)) for row in currency_rates_query}

        # Get all site history
        sites_data = db.session.query(
            SiteHistory.amount,
            SiteHistory.currency,
            SiteHistory.recorded_at,
            Sites.name
        ).join(Sites, SiteHistory.site_id == Sites.id)\
         .filter(SiteHistory.user_id == current_user.id).all()

        # Get all asset history
        assets_data = db.session.query(
            AssetHistory.amount,
            AssetHistory.currency,
            AssetHistory.recorded_at,
            Assets.name
        ).join(Assets, AssetHistory.asset_id == Assets.id)\
         .filter(AssetHistory.user_id == current_user.id).all()

        all_data_points = []
        for row in sites_data:
            amount_usd = Decimal(str(row.amount)) / currency_rates.get(row.currency, Decimal('1.0'))
            all_data_points.append({
                'date': row.recorded_at,
                'amount_usd': amount_usd,
                'name': row.name,
                'type': 'site'
            })
        for row in assets_data:
            amount_usd = Decimal(str(row.amount)) / currency_rates.get(row.currency, Decimal('1.0'))
            all_data_points.append({
                'date': row.recorded_at,
                'amount_usd': amount_usd,
                'name': row.name,
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
        # Get currency rates
        currency_rates_query = db.session.query(Currency.code, Currency.rate).all()
        currency_rates = {row.code: Decimal(str(row.rate)) for row in currency_rates_query}

        # Get all site history
        sites_data = db.session.query(
            SiteHistory.amount, SiteHistory.currency, SiteHistory.recorded_at, Sites.name
        ).join(Sites, SiteHistory.site_id == Sites.id)\
         .filter(SiteHistory.user_id == current_user.id)\
         .order_by(SiteHistory.recorded_at).all()

        if not sites_data:
            return jsonify({'datasets': []})

        # Group data by site
        site_data_points = {}
        all_dates = set()
        for row in sites_data:
            site_name = row.name
            date = row.recorded_at
            amount_usd = Decimal(str(row.amount)) / currency_rates.get(row.currency, Decimal('1.0'))
            if site_name not in site_data_points:
                site_data_points[site_name] = []
            site_data_points[site_name].append({
                'date': date,
                'amount_usd': amount_usd
            })
            all_dates.add(date.date())

        if not all_dates:
            return jsonify({'datasets': []})

        # Determine the full date range for the chart's x-axis
        min_day = min(all_dates)
        max_day = max(all_dates)
        
        # This logic is for Chart.js time cartesian axis, which uses {x, y} data points
        # instead of separate labels and data arrays. This is more robust for time-series data.
        # The frontend will need to be adjusted to handle this data format.
        # However, to minimize changes, we will stick to the labels/data format for now,
        # but generate it more robustly.

        date_range = []
        current_day = min_day
        while current_day <= max_day:
            date_range.append(current_day)
            current_day += timedelta(days=1)

        labels = [d.isoformat() for d in date_range]
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
            # points are already sorted by recorded_at from the query
            data = []
            point_index = 0
            last_known_value = Decimal('0.0')

            for day in date_range:
                # Find the last update for this site on or before the current day
                todays_points = [p for p in points if p['date'].date() == day]

                if todays_points:
                    # If there are updates today, use the last one
                    last_known_value = todays_points[-1]['amount_usd']
                elif not data:
                    # If it's the first day and no data, check for previous data
                    previous_points = [p for p in points if p['date'].date() < day]
                    if previous_points:
                        last_known_value = previous_points[-1]['amount_usd']

                # Append the value for the day (either new or carried over)
                data.append(float(round(last_known_value, 2)))

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
            'datasets': datasets
        })
    except Exception as e:
        current_app.logger.error(f"Error in get_poker_sites_historical_data: {e}")
        return jsonify({'error': str(e)}), 500

@charts_bp.route("/assets_historical_data")
@login_required
def get_assets_historical_data():
    try:
        currency_rates_query = db.session.query(Currency.code, Currency.rate).all()
        currency_rates = {row.code: Decimal(str(row.rate)) for row in currency_rates_query}

        assets_data = db.session.query(
            AssetHistory.amount, AssetHistory.currency, AssetHistory.recorded_at, Assets.name
        ).join(Assets, AssetHistory.asset_id == Assets.id)\
         .filter(AssetHistory.user_id == current_user.id)\
         .order_by(AssetHistory.recorded_at).all()

        if not assets_data:
            return jsonify({'labels': [], 'datasets': []})

        asset_data_points = {}
        dates = set()
        for row in assets_data:
            asset_name = row.name
            date = row.recorded_at.date()
            amount_usd = Decimal(str(row.amount)) / currency_rates.get(row.currency, Decimal('1.0'))
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
        currency_rates_query = db.session.query(Currency.code, Currency.rate).all()
        currency_rates = {row.code: Decimal(str(row.rate)) for row in currency_rates_query}

        assets_data = db.session.query(
            AssetHistory.asset_id, AssetHistory.amount, AssetHistory.currency, Assets.name
        ).join(Assets, AssetHistory.asset_id == Assets.id)\
         .filter(AssetHistory.user_id == current_user.id)\
         .order_by(AssetHistory.recorded_at.desc()).all()

        latest_asset_values = {}
        for row in assets_data:
            asset_id = row.asset_id
            if asset_id not in latest_asset_values:
                latest_asset_values[asset_id] = {
                    'name': row.name,
                    'amount_usd': Decimal(str(row.amount)) / currency_rates.get(row.currency, Decimal('1.0'))
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
        # Get currency rates
        currency_rates_query = db.session.query(Currency.code, Currency.rate).all()
        currency_rates = {row.code: Decimal(str(row.rate)) for row in currency_rates_query}

        # Get all site history
        sites_data = db.session.query(
            SiteHistory.amount, SiteHistory.currency, SiteHistory.recorded_at, Sites.name
        ).join(Sites, SiteHistory.site_id == Sites.id)\
         .filter(SiteHistory.user_id == current_user.id).all()

        # Get all asset history
        assets_data = db.session.query(
            AssetHistory.amount, AssetHistory.currency, AssetHistory.recorded_at, Assets.name
        ).join(Assets, AssetHistory.asset_id == Assets.id)\
         .filter(AssetHistory.user_id == current_user.id).all()

        # Get all deposits
        deposits_data = db.session.query(Deposits.amount, Deposits.currency, Deposits.date)\
            .filter(Deposits.user_id == current_user.id).all()

        # Get all withdrawals
        withdrawals_data = db.session.query(Drawings.amount, Drawings.currency, Drawings.date)\
            .filter(Drawings.user_id == current_user.id).all()

        all_financial_events = []

        # Add site history
        for row in sites_data:
            amount_usd = Decimal(str(row.amount)) / currency_rates.get(row.currency, Decimal('1.0'))
            all_financial_events.append({
                'date': row.recorded_at,
                'type': 'bankroll_update',
                'name': row.name,
                'entity_type': 'site',
                'amount_usd': amount_usd
            })

        # Add asset history as bankroll changes
        for row in assets_data:
            amount_usd = Decimal(str(row.amount)) / currency_rates.get(row.currency, Decimal('1.0'))
            all_financial_events.append({
                'date': row.recorded_at,
                'type': 'bankroll_update',
                'name': row.name,
                'entity_type': 'asset',
                'amount_usd': amount_usd
            })

        # Add deposits
        for row in deposits_data:
            amount_usd = Decimal(str(row.amount)) / currency_rates.get(row.currency, Decimal('1.0'))
            all_financial_events.append({
                'date': row.date,
                'type': 'deposit',
                'amount_usd': amount_usd
            })

        # Add withdrawals
        for row in withdrawals_data:
            amount_usd = Decimal(str(row.amount)) / currency_rates.get(row.currency, Decimal('1.0'))
            all_financial_events.append({
                'date': row.date,
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
        currency_rates_query = db.session.query(Currency.code, Currency.rate).all()
        currency_rates = {row.code: Decimal(str(row.rate)) for row in currency_rates_query}

        withdrawals_raw = db.session.query(Drawings.amount, Drawings.currency, Drawings.date)\
            .filter(Drawings.user_id == current_user.id).order_by(Drawings.date).all()

        if not withdrawals_raw:
            return jsonify({'labels': [], 'datasets': []})

        withdrawals_by_date = {}
        dates = set()
        for row in withdrawals_raw:
            date = row.date.date()
            amount_usd = Decimal(str(row.amount)) / currency_rates.get(row.currency, Decimal('1.0'))
            
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
        currency_rates_query = db.session.query(Currency.code, Currency.rate).all()
        currency_rates = {row.code: Decimal(str(row.rate)) for row in currency_rates_query}

        deposits_raw = db.session.query(Deposits.amount, Deposits.currency, Deposits.date)\
            .filter(Deposits.user_id == current_user.id).order_by(Deposits.date).all()

        if not deposits_raw:
            return jsonify({'labels': [], 'datasets': []})

        deposits_by_date = {}
        dates = set()
        for row in deposits_raw:
            date = row.date.date()
            amount_usd = Decimal(str(row.amount)) / currency_rates.get(row.currency, Decimal('1.0'))
            
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
        currency_rates_query = db.session.query(Currency.code, Currency.rate).all()
        currency_rates = {row.code: Decimal(str(row.rate)) for row in currency_rates_query}

        sites_data = db.session.query(
            SiteHistory.site_id, SiteHistory.amount, SiteHistory.currency, Sites.name
        ).join(Sites, SiteHistory.site_id == Sites.id)\
         .filter(SiteHistory.user_id == current_user.id)\
         .order_by(SiteHistory.recorded_at.desc()).all()

        latest_site_values = {}
        for row in sites_data:
            site_id = row.site_id
            if site_id not in latest_site_values:
                latest_site_values[site_id] = {
                    'name': row.name,
                    'amount_usd': Decimal(str(row.amount)) / currency_rates.get(row.currency, Decimal('1.0'))
                }

        labels = [value['name'] for value in latest_site_values.values()]
        data = [float(round(value['amount_usd'], 2)) for value in latest_site_values.values()]

        return jsonify({'labels': labels, 'datasets': [{'data': data}]})

    except Exception as e:
        current_app.logger.error(f"Error in get_poker_sites_pie_data: {e}")
        return jsonify({'error': str(e)}), 500