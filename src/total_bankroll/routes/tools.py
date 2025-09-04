import json
import os
from flask import Blueprint, render_template, request, current_app
from flask_security import current_user, login_required
from decimal import Decimal, InvalidOperation
from ..utils import get_user_bankroll_data
from ..recommendations import RecommendationEngine

tools_bp = Blueprint('tools', __name__)

def parse_currency_to_decimal(currency_str):
    """Helper to parse currency string to Decimal."""
    return Decimal(str(currency_str).replace('$', '').replace(',', ''))

@tools_bp.route('/tools')
@login_required
def tools_page():
    return render_template('tools.html')

def _get_user_selections(request_args):
    """Extracts and maps user filter selections from request arguments."""
    game_type_map = {
        'limit_holdem': "Limit Hold’Em",
        'nlhe': "NLHE",
        'plo': "PLO",
        'na': "NA"
    }
    skill_level_map = {
        'soft': "Soft Games",
        'tough': "Tough Games",
        'na': "NA"
    }
    risk_tolerance_map = {
        'conservative': "Conservative",
        'aggressive': "Aggressive",
        'na': "NA"
    }
    game_environment_map = {
        'live': "Live Poker",
        'online': "Online Poker",
        'na': "NA"
    }
    return {
        'game_type': game_type_map.get(request_args.get('game_type', 'nlhe')),
        'skill_level': skill_level_map.get(request_args.get('skill_level', 'tough')),
        'risk_tolerance': risk_tolerance_map.get(request_args.get('risk_tolerance', 'conservative')),
        'game_environment': game_environment_map.get(request_args.get('game_environment', 'online'))
    }

@tools_bp.route('/poker_stakes')
@login_required
def poker_stakes_page():
    # Get user selections and bankroll
    selections = _get_user_selections(request.args)
    bankroll_data = get_user_bankroll_data(current_user.id)
    total_bankroll = bankroll_data['total_bankroll']
    
    # Initialize the recommendation engine
    engine = RecommendationEngine()
    range_data = engine._calculate_weighted_range(selections, 'cash_games')
    buy_in_multiple = range_data['average_multiple']

    # Load cash game stakes data from JSON
    cash_stakes_json_path = os.path.join(current_app.root_path, 'data', 'cash_game_stakes.json')
    with open(cash_stakes_json_path, 'r') as f:
        cash_stakes_data = json.load(f)
    stakes_list = cash_stakes_data['stakes']

    # Calculate all recommendation messages
    recommendations = engine.get_cash_game_recommendation_data(selections, total_bankroll, stakes_list)
    recommended_stake_index = recommendations['recommended_stake_index']

    # Reconstruct the table in the list-of-lists format expected by the template
    headers = ["Small Blind", "Big Blind", "Minimum Buy-In", "Maximum Buy-In", "Bankroll Required", "Additional $ Required"]
    cash_stakes_table = [headers]
    for i, stake in enumerate(stakes_list):
        max_buy_in = parse_currency_to_decimal(stake['max_buy_in'])

        bankroll_required = Decimal('0.0')
        if buy_in_multiple > 0:
            bankroll_required = max_buy_in * buy_in_multiple

        additional_required = bankroll_required - total_bankroll

        # For stakes lower than recommended, show the negative "additional required" to indicate the buffer.
        # For the recommended stake and higher, clamp to zero if the user is already rolled.
        if recommended_stake_index != -1 and i < recommended_stake_index:
            pass  # Keep the negative value for stakes below the recommended one
        elif additional_required < 0:
            additional_required = Decimal('0.0')

        cash_stakes_table.append([
            stake['small_blind'],
            stake['big_blind'],
            stake['min_buy_in'],
            stake['max_buy_in'],
            f"${bankroll_required:,.2f}",
            f"${additional_required:,.2f}"
        ])

    return render_template(
        'poker_stakes.html',
        total_bankroll=total_bankroll,
        cash_stakes_table=cash_stakes_table,
        **recommendations,
        bankroll_recommendation=range_data['recommendation_string'],
        # Pass filter values to template
        game_type=request.args.get('game_type', 'nlhe'),
        skill_level=request.args.get('skill_level', 'tough'),
        risk_tolerance=request.args.get('risk_tolerance', 'conservative'),
        game_environment=request.args.get('game_environment', 'online')
    )

@tools_bp.route('/tournament_stakes')
@login_required
def tournament_stakes_page():
    """Tournament Stakes page."""
    selections = _get_user_selections(request.args)
    site_filter = request.args.get('site_filter', 'all')
    
    # Initialize the recommendation engine
    engine = RecommendationEngine()

    # Load tournament buy-in data from JSON
    json_path = os.path.join(current_app.root_path, 'data', 'tournament_buy_ins.json')
    with open(json_path, 'r') as f:
        tournament_buy_ins = json.load(f)

    # Calculate range and mean buy-ins
    range_data = engine._calculate_weighted_range(selections, 'tournaments')
    mean_buy_ins = range_data['average_multiple']

    bankroll_data = get_user_bankroll_data(current_user.id)
    total_bankroll = bankroll_data['total_bankroll']

    # --- Add new columns to tournament_buy_ins data ---
    for site_key, site_data in tournament_buy_ins.items():
        if 'buy_ins' in site_data:
            for item in site_data['buy_ins']:
                buy_in_str = item.get('buy_in')
                if not buy_in_str:
                    item['bankroll_required'] = '$0.00'
                    item['additional_required'] = '$0.00'
                    item['buy_in_dec'] = Decimal('0.0')
                    continue
                
                try:
                    buy_in_dec = parse_currency_to_decimal(buy_in_str)
                    item['buy_in_dec'] = buy_in_dec
                    
                    bankroll_required = Decimal('0.0')
                    if mean_buy_ins > 0:
                        bankroll_required = buy_in_dec * mean_buy_ins
                    
                    additional_required = bankroll_required - total_bankroll
                    if additional_required < 0:
                        additional_required = Decimal('0.0')
                    
                    item['bankroll_required'] = f"${bankroll_required:,.2f}"
                    item['additional_required'] = f"${additional_required:,.2f}"
                except (ValueError, InvalidOperation):
                    item['bankroll_required'] = 'N/A'
                    item['additional_required'] = 'N/A'
                    item['buy_in_dec'] = None

    # --- Calculate recommendations and display columns ---
    # First, calculate per-site recommendations to determine the recommended stake for each table.
    for site_key, site_data in tournament_buy_ins.items():
        if 'buy_ins' in site_data:
            # Pass 1: Populate 'buy_in_dec' and build a map for the recommendation engine.
            site_buyins_map = {}
            for item in site_data['buy_ins']:
                buy_in_str = item.get('buy_in')
                if not buy_in_str:
                    item['buy_in_dec'] = Decimal('0.0')
                    continue
                try:
                    buy_in_dec = parse_currency_to_decimal(buy_in_str)
                    item['buy_in_dec'] = buy_in_dec
                    if buy_in_dec not in site_buyins_map:
                        site_buyins_map[buy_in_dec] = buy_in_str
                except (ValueError, InvalidOperation):
                    item['buy_in_dec'] = None
            
            # Calculate the recommendation for this specific site.
            site_recommendations = engine.get_tournament_recommendation_data(selections, total_bankroll, site_buyins_map)
            site_data['recommendations'] = site_recommendations
            recommended_stake_dec = site_recommendations.get('recommended_tournament_stake_dec')

            # Pass 2: Populate the display columns ('Bankroll Required', 'Additional $ Required')
            # using the per-site recommendation to apply the correct logic.
            for item in site_data['buy_ins']:
                buy_in_dec = item.get('buy_in_dec')
                if buy_in_dec is None:
                    item['bankroll_required'] = 'N/A'
                    item['additional_required'] = 'N/A'
                    continue

                bankroll_required = buy_in_dec * mean_buy_ins if mean_buy_ins > 0 else Decimal('0.0')
                additional_required = bankroll_required - total_bankroll

                # For stakes lower than recommended, show the negative "additional required"
                # to indicate the buffer. For higher stakes, clamp to zero.
                if recommended_stake_dec is not None and buy_in_dec < recommended_stake_dec:
                    pass  # Keep the negative value
                elif additional_required < 0:
                    additional_required = Decimal('0.0')

                item['bankroll_required'] = f"${bankroll_required:,.2f}"
                item['additional_required'] = f"${additional_required:,.2f}"

    # --- Calculate Global Recommendation for top messages ---
    # This uses all sites if filter is 'all', or the specific site if filtered.
    global_buyins_map = {}
    sites_to_process_for_global = {}
    if site_filter == 'all':
        sites_to_process_for_global = tournament_buy_ins
    elif site_filter in tournament_buy_ins:
        sites_to_process_for_global = {site_filter: tournament_buy_ins[site_filter]}

    for site_data in sites_to_process_for_global.values():
        for item in site_data.get('buy_ins', []):
            buy_in_dec = item.get('buy_in_dec')
            buy_in_str = item.get('buy_in')
            if buy_in_dec is not None and buy_in_str is not None and buy_in_dec not in global_buyins_map:
                global_buyins_map[buy_in_dec] = buy_in_str

    # Calculate recommendations using the new engine
    global_recommendations = engine.get_tournament_recommendation_data(
        selections, total_bankroll, global_buyins_map
    )

    return render_template('tournament_stakes.html',
                           total_bankroll=total_bankroll,
                           game_type=request.args.get('game_type', 'nlhe'),
                           skill_level=request.args.get('skill_level', 'tough'),
                           risk_tolerance=request.args.get('risk_tolerance', 'conservative'),
                           game_environment=request.args.get('game_environment', 'online'),
                           tournament_bankroll_recommendation=range_data['recommendation_string'],
                           **global_recommendations,
                           site_filter=site_filter,
                           tournament_buy_ins=tournament_buy_ins
                           )