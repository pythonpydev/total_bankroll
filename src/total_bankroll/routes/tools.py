import json
import os
from flask import Blueprint, render_template, request, current_app
from flask_security import current_user, login_required
from decimal import Decimal, InvalidOperation
from ..utils import get_user_bankroll_data

tools_bp = Blueprint('tools', __name__)

def parse_currency_to_decimal(currency_str):
    """Helper to parse currency string to Decimal."""
    return Decimal(str(currency_str).replace('$', '').replace(',', ''))

@tools_bp.route('/tools')
def tools_page():
    return render_template('tools.html')

def _calculate_weighted_range(game_type, skill_level, risk_tolerance, game_environment, 
                              game_type_ranges, skill_level_ranges, risk_tolerance_ranges, game_environment_ranges, unit_string):
    """Generic function to calculate a weighted bankroll range."""
    # Retrieve low and high for each selection
    low_gt, high_gt = game_type_ranges.get(game_type, (0, 0))
    low_sl, high_sl = skill_level_ranges.get(skill_level, (0, 0))
    low_rt, high_rt = risk_tolerance_ranges.get(risk_tolerance, (0, 0))
    low_ge, high_ge = game_environment_ranges.get(game_environment, (0, 0))
    
    # Set weights, 0 for NA selections
    weight_gt = 2 if game_type != "NA" else 0
    weight_sl = 3 if skill_level != "NA" else 0
    weight_rt = 4 if risk_tolerance != "NA" else 0
    weight_ge = 1 if game_environment != "NA" else 0
    total_weight = weight_gt + weight_sl + weight_rt + weight_ge
    
    # Calculate weighted averages
    if total_weight > 0:
        weighted_low = (low_gt * weight_gt) + (low_sl * weight_sl) + (low_rt * weight_rt) + (low_ge * weight_ge)
        weighted_high = (high_gt * weight_gt) + (high_sl * weight_sl) + (high_rt * weight_rt) + (high_ge * weight_ge)
        average_low = round(weighted_low / total_weight)
        average_high = round(weighted_high / total_weight)
    else:
        average_low = 0
        average_high = 0
    
    return f"{average_low} to {average_high} {unit_string}"

def calculate_bankroll_range(game_type, skill_level, risk_tolerance, game_environment):
    """Calculates the recommended bankroll range in big blinds based on user inputs."""
    game_type_ranges = {
        "Limit Hold’Em": (20, 30), "NLHE": (30, 50), "PLO": (50, 100), "NA": (0, 0)
    }
    skill_level_ranges = {
        "Soft Games": (20, 30), "Tough Games": (50, 100), "NA": (0, 0)
    }
    risk_tolerance_ranges = {
        "Conservative": (50, 100), "Aggressive": (20, 30), "NA": (0, 0)
    }
    game_environment_ranges = {
        "Live Poker": (20, 30), "Online Poker": (40, 60), "NA": (0, 0)
    }
    return _calculate_weighted_range(
        game_type, skill_level, risk_tolerance, game_environment,
        game_type_ranges, skill_level_ranges, risk_tolerance_ranges, game_environment_ranges,
        "big blinds"
    )

def calculate_tournament_bankroll_range(game_type, skill_level, risk_tolerance, game_environment):
    """Calculates the recommended tournament bankroll range in number of buy-ins."""
    game_type_ranges = {
        "Limit Hold’Em": (40, 60), "NLHE": (60, 100), "PLO": (100, 200), "NA": (0, 0)
    }
    skill_level_ranges = {
        "Soft Games": (40, 60), "Tough Games": (100, 200), "NA": (0, 0)
    }
    risk_tolerance_ranges = {
        "Conservative": (100, 200), "Aggressive": (40, 60), "NA": (0, 0)
    }
    game_environment_ranges = {
        "Live Poker": (40, 60), "Online Poker": (80, 120), "NA": (0, 0)
    }
    return _calculate_weighted_range(
        game_type, skill_level, risk_tolerance, game_environment,
        game_type_ranges, skill_level_ranges, risk_tolerance_ranges, game_environment_ranges,
        "buy-ins"
    )

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

def _get_buy_in_multiple_from_recommendation(recommendation_str):
    """Parses a recommendation string (e.g., '44 to 86 big blinds') to get a mean value."""
    buy_in_multiple = Decimal('30.0')  # Default value
    try:
        parts = recommendation_str.split()
        low = int(parts[0])
        high = int(parts[2])
        if high > 0:
            buy_in_multiple = (Decimal(low) + Decimal(high)) / Decimal('2.0')
        else:
            buy_in_multiple = Decimal('0.0')
    except (ValueError, IndexError):
        buy_in_multiple = Decimal('30.0')
    return buy_in_multiple

def _calculate_cash_game_recommendations(total_bankroll, buy_in_multiple, cash_stakes_table):
    """Calculates all recommendation messages for cash games."""
    recommendations = {
        "recommended_stake": "N/A",
        "stake_explanation": "",
        "next_stake_level": "",
        "next_stake_message": "",
        "move_down_stake_level": "",
        "move_down_message": ""
    }

    if buy_in_multiple <= 0:
        recommendations["stake_explanation"] = "Please make selections above to get a stake recommendation."
        return recommendations

    # Find recommended stake
    recommended_stake_index = -1
    for i in range(len(cash_stakes_table) - 1, 0, -1):
        stake_row = cash_stakes_table[i]
        max_buy_in = parse_currency_to_decimal(stake_row[3])
        if total_bankroll >= buy_in_multiple * max_buy_in:
            recommendations["recommended_stake"] = f"{stake_row[0]}/{stake_row[1]}"
            recommendations["stake_explanation"] = (
                f"Based on your bankroll of ${total_bankroll:.2f}, you have {total_bankroll / max_buy_in:.1f} "
                f"buy-ins for {stake_row[0]}/{stake_row[1]} stakes. With the recommended {buy_in_multiple:.0f} "
                f"buy-in rule, you can comfortably play at these stakes."
            )
            recommended_stake_index = i
            break
    else:
        # Handle case where bankroll is below the smallest stake
        smallest_stake_row = cash_stakes_table[1]
        smallest_min_buy_in = parse_currency_to_decimal(smallest_stake_row[2])
        if total_bankroll < buy_in_multiple * smallest_min_buy_in:
            recommendations["recommended_stake"] = "Below Smallest Stakes"
            recommendations["stake_explanation"] = (
                f"Your bankroll of ${total_bankroll:.2f} is less than {buy_in_multiple:.0f} times the minimum buy-in "
                f"for the smallest available stakes ({smallest_stake_row[0]}/{smallest_stake_row[1]}). "
                f"Consider depositing more funds to comfortably play at these stakes."
            )
            recommendations["next_stake_level"] = f"{smallest_stake_row[0]}/{smallest_stake_row[1]}"

    if recommended_stake_index == -1:
        return recommendations

    # Calculate "move up" message
    if recommended_stake_index < len(cash_stakes_table) - 1:
        next_stake_row = cash_stakes_table[recommended_stake_index + 1]
        recommendations["next_stake_level"] = f"{next_stake_row[0]}/{next_stake_row[1]}"
        next_stake_max_buy_in = parse_currency_to_decimal(next_stake_row[3])
        required_bankroll = buy_in_multiple * next_stake_max_buy_in
        additional_needed = required_bankroll - total_bankroll
        if additional_needed > 0:
            recommendations["next_stake_message"] = (
                f"To move up to {recommendations['next_stake_level']} stakes, you need to win an additional "
                f"${additional_needed:.2f} to reach a bankroll of ${required_bankroll:.2f}."
            )

    # Calculate "move down" message
    if recommended_stake_index > 1:
        move_down_stake_row = cash_stakes_table[recommended_stake_index - 1]
        recommendations["move_down_stake_level"] = f"{move_down_stake_row[0]}/{move_down_stake_row[1]}"
        
        # Corrected logic for move down threshold
        current_stake_row = cash_stakes_table[recommended_stake_index]
        current_max_buy_in = parse_currency_to_decimal(current_stake_row[3])
        move_down_bankroll_threshold = buy_in_multiple * current_max_buy_in
        amount_can_lose = total_bankroll - move_down_bankroll_threshold

        if amount_can_lose >= 0:
            recommendations["move_down_message"] = (
                f"You will need to move down to {recommendations['move_down_stake_level']} stakes if you lose "
                f"${amount_can_lose:.2f} to drop to a bankroll of ${move_down_bankroll_threshold:.2f}."
            )

    return recommendations

def _calculate_tournament_recommendations(total_bankroll, mean_buy_ins, all_buyins_str, tournament_stakes_list_dec):
    """Calculates all recommendation messages for tournaments."""
    recs = {
        "recommended_tournament_stake": "N/A",
        "stake_explanation": "",
        "next_stake_level": "",
        "next_stake_message": "",
        "move_down_stake_level": "",
        "move_down_message": "",
        "recommended_buy_in": Decimal('0.0'),
        "recommended_tournament_stake_dec": None,
        "next_stake_level_dec": None,
        "move_down_stake_level_dec": None
    }

    if mean_buy_ins <= 0:
        recs["stake_explanation"] = "Please make selections above to get a stake recommendation."
        return recs

    recs["recommended_buy_in"] = total_bankroll / mean_buy_ins

    # Find the recommended tournament stake
    found_stake_index = -1
    for i in range(len(tournament_stakes_list_dec) - 1, -1, -1):
        stake_dec = tournament_stakes_list_dec[i]
        if stake_dec <= recs["recommended_buy_in"]:
            found_stake_index = i
            break
    
    if found_stake_index != -1:
        current_stake_dec = tournament_stakes_list_dec[found_stake_index]
        recs["recommended_tournament_stake"] = all_buyins_str[found_stake_index]
        recs["recommended_tournament_stake_dec"] = current_stake_dec
        
        num_buy_ins_for_stake = total_bankroll / current_stake_dec if current_stake_dec > 0 else Decimal('inf')
        
        recs["stake_explanation"] = (
            f"Based on your bankroll of ${total_bankroll:.2f} and the recommended {mean_buy_ins:.0f} buy-in rule, "
            f"your average buy-in should be ${recs['recommended_buy_in']:.2f}. The closest standard buy-in you can play is "
            f"{recs['recommended_tournament_stake']}, for which you have {num_buy_ins_for_stake:.1f} buy-ins."
        )

        # Move up logic
        if found_stake_index < len(all_buyins_str) - 1:
            recs["next_stake_level"] = all_buyins_str[found_stake_index + 1]
            next_stake_dec = tournament_stakes_list_dec[found_stake_index + 1]
            recs["next_stake_level_dec"] = next_stake_dec
            required_bankroll_for_next_stake = next_stake_dec * mean_buy_ins
            additional_bankroll_needed = required_bankroll_for_next_stake - total_bankroll

            if additional_bankroll_needed > 0:
                recs["next_stake_message"] = f"To move up to {recs['next_stake_level']} tournaments, you need to win or deposit an additional ${additional_bankroll_needed:.2f} to reach a bankroll of ${required_bankroll_for_next_stake:.2f}."
            else:
                recs["next_stake_message"] = f"You are already sufficiently rolled to start playing at {recs['next_stake_level']} tournaments."

        # Move down logic
        if found_stake_index > 0:
            recs["move_down_stake_level"] = all_buyins_str[found_stake_index - 1]
            recs["move_down_stake_level_dec"] = tournament_stakes_list_dec[found_stake_index - 1]
            current_stake_required_br = current_stake_dec * mean_buy_ins
            amount_can_lose = total_bankroll - current_stake_required_br
            recs["move_down_message"] = f"You will need to move down to {recs['move_down_stake_level']} tournaments if you lose ${amount_can_lose:.2f} to drop to a bankroll of ${current_stake_required_br:.2f}."
    else: # Below smallest stakes
        recs["recommended_tournament_stake"] = "Below Smallest Stakes"
        recs["stake_explanation"] = f"Your bankroll of ${total_bankroll:.2f} is too small for the lowest available stakes based on the recommended {mean_buy_ins:.0f} buy-in rule. Your average buy-in should be ${recs['recommended_buy_in']:.2f}."
        if all_buyins_str:
            recs["next_stake_level"] = all_buyins_str[0]
            next_stake_dec = tournament_stakes_list_dec[0]
            recs["next_stake_level_dec"] = next_stake_dec
            required_bankroll_for_next_stake = next_stake_dec * mean_buy_ins
            additional_bankroll_needed = required_bankroll_for_next_stake - total_bankroll
            recs["next_stake_message"] = f"To play at the lowest stakes ({recs['next_stake_level']}), you need to win or deposit an additional ${additional_bankroll_needed:.2f} to reach a bankroll of ${required_bankroll_for_next_stake:.2f}."
            
    return recs

@tools_bp.route('/poker_stakes')
@login_required
def poker_stakes_page():
    # Get user selections and bankroll
    selections = _get_user_selections(request.args)
    bankroll_data = get_user_bankroll_data(current_user.id)
    total_bankroll = bankroll_data['total_bankroll']

    # Calculate bankroll recommendation
    bankroll_recommendation = calculate_bankroll_range(
        selections['game_type'], selections['skill_level'], 
        selections['risk_tolerance'], selections['game_environment']
    )

    # Parse the bankroll recommendation to get the mean buy-in multiple
    buy_in_multiple = _get_buy_in_multiple_from_recommendation(bankroll_recommendation)

    # Load cash game stakes data from JSON
    cash_stakes_json_path = os.path.join(current_app.root_path, 'data', 'cash_game_stakes.json')
    with open(cash_stakes_json_path, 'r') as f:
        cash_stakes_data = json.load(f)

    stakes_list = cash_stakes_data['stakes']

    # Find the recommended stake index from the raw data first, so we can use it for display logic.
    recommended_stake_index = -1
    if buy_in_multiple > 0:
        for i in range(len(stakes_list) - 1, -1, -1):
            stake_row = stakes_list[i]
            max_buy_in = parse_currency_to_decimal(stake_row['max_buy_in'])
            if total_bankroll >= buy_in_multiple * max_buy_in:
                recommended_stake_index = i
                break

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

    # Calculate all recommendation messages
    recommendations = _calculate_cash_game_recommendations(total_bankroll, buy_in_multiple, cash_stakes_table)

    return render_template(
        'poker_stakes.html',
        total_bankroll=total_bankroll,
        cash_stakes_table=cash_stakes_table,
        **recommendations,
        bankroll_recommendation=bankroll_recommendation,
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

    # Load tournament buy-in data from JSON
    json_path = os.path.join(current_app.root_path, 'data', 'tournament_buy_ins.json')
    with open(json_path, 'r') as f:
        tournament_buy_ins = json.load(f)

    tournament_bankroll_recommendation = calculate_tournament_bankroll_range(
        selections['game_type'], selections['skill_level'],
        selections['risk_tolerance'], selections['game_environment']
    )

    mean_buy_ins = Decimal('0.0')
    try:
        parts = tournament_bankroll_recommendation.split()
        low = int(parts[0])
        high = int(parts[2])
        if high > 0:
            mean_buy_ins = (Decimal(low) + Decimal(high)) / Decimal('2.0')
    except (ValueError, IndexError):
        mean_buy_ins = Decimal('0.0')

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
            site_stakes_list_dec = sorted(site_buyins_map.keys())
            site_all_buyins_str = [site_buyins_map[d] for d in site_stakes_list_dec]
            site_recommendations = _calculate_tournament_recommendations(total_bankroll, mean_buy_ins, site_all_buyins_str, site_stakes_list_dec)
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

    global_stakes_list_dec = sorted(global_buyins_map.keys())
    global_all_buyins_str = [global_buyins_map[d] for d in global_stakes_list_dec]

    global_recommendations = _calculate_tournament_recommendations(
        total_bankroll, mean_buy_ins, global_all_buyins_str, global_stakes_list_dec
    )

    return render_template('tournament_stakes.html',
                           total_bankroll=total_bankroll,
                           game_type=request.args.get('game_type', 'nlhe'),
                           skill_level=request.args.get('skill_level', 'tough'),
                           risk_tolerance=request.args.get('risk_tolerance', 'conservative'),
                           game_environment=request.args.get('game_environment', 'online'),
                           tournament_bankroll_recommendation=tournament_bankroll_recommendation,
                           **global_recommendations,
                           site_filter=site_filter,
                           tournament_buy_ins=tournament_buy_ins
                           )