import json
import os
from flask import Blueprint, render_template, request, current_app
from flask_security import current_user, login_required
from decimal import Decimal
from ..utils import get_user_bankroll_data

tools_bp = Blueprint('tools', __name__)

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
    # Function to parse currency string to Decimal
    def parse_currency_to_decimal(currency_str):
        return Decimal(currency_str.replace('$', '').replace(',', ''))

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
        max_buy_in = parse_currency_to_decimal(stake_row[4])
        if total_bankroll >= buy_in_multiple * max_buy_in:
            recommendations["recommended_stake"] = f"{stake_row[1]}/{stake_row[2]}"
            recommendations["stake_explanation"] = (
                f"Based on your bankroll of ${total_bankroll:.2f}, you have {total_bankroll / max_buy_in:.1f} "
                f"buy-ins for {stake_row[1]}/{stake_row[2]} stakes. With the recommended {buy_in_multiple:.0f} "
                f"buy-in rule, you can comfortably play at these stakes."
            )
            recommended_stake_index = i
            break
    else:
        # Handle case where bankroll is below the smallest stake
        smallest_stake_row = cash_stakes_table[1]
        smallest_min_buy_in = parse_currency_to_decimal(smallest_stake_row[3])
        if total_bankroll < buy_in_multiple * smallest_min_buy_in:
            recommendations["recommended_stake"] = "Below Smallest Stakes"
            recommendations["stake_explanation"] = (
                f"Your bankroll of ${total_bankroll:.2f} is less than {buy_in_multiple:.0f} times the minimum buy-in "
                f"for the smallest available stakes ({smallest_stake_row[1]}/{smallest_stake_row[2]}). "
                f"Consider depositing more funds to comfortably play at these stakes."
            )
            recommendations["next_stake_level"] = f"{smallest_stake_row[1]}/{smallest_stake_row[2]}"

    if recommended_stake_index == -1:
        return recommendations

    # Calculate "move up" message
    if recommended_stake_index < len(cash_stakes_table) - 1:
        next_stake_row = cash_stakes_table[recommended_stake_index + 1]
        recommendations["next_stake_level"] = f"{next_stake_row[1]}/{next_stake_row[2]}"
        next_stake_max_buy_in = parse_currency_to_decimal(next_stake_row[4])
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
        recommendations["move_down_stake_level"] = f"{move_down_stake_row[1]}/{move_down_stake_row[2]}"
        move_down_threshold_max_buy_in = parse_currency_to_decimal(move_down_stake_row[4])
        required_bankroll_to_stay = buy_in_multiple * move_down_threshold_max_buy_in
        amount_can_lose = total_bankroll - required_bankroll_to_stay
        if amount_can_lose >= 0:
            recommendations["move_down_message"] = (
                f"You will need to move down to {recommendations['move_down_stake_level']} stakes if you lose "
                f"${amount_can_lose:.2f} to drop to a bankroll of ${required_bankroll_to_stay:.2f}."
            )

    return recommendations

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

    # Reconstruct the table in the list-of-lists format expected by the template
    headers = ["ID", "Small Blind", "Big Blind", "Minimum Buy-In", "Maximum Buy-In"]
    cash_stakes_table = [headers]
    for stake in cash_stakes_data['stakes']:
        cash_stakes_table.append([
            stake['id'],
            stake['small_blind'],
            stake['big_blind'],
            stake['min_buy_in'],
            stake['max_buy_in']
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

    # --- Tournament Stake Recommendation Logic ---
    # Dynamically build the list of all tournament buy-ins from the JSON data
    all_buyins_map = {}  # Use a map to store {Decimal: str} to handle sorting and keep original format
    for site_data in tournament_buy_ins.values():
        for item in site_data.get('buy_ins', []):
            buy_in_str = item.get('buy_in')
            if not buy_in_str:
                continue
            try:
                buy_in_dec = Decimal(buy_in_str.replace('$', '').replace(',', ''))
                if buy_in_dec not in all_buyins_map:
                    all_buyins_map[buy_in_dec] = buy_in_str
            except Exception:
                current_app.logger.warning(f"Could not parse buy-in '{buy_in_str}' to Decimal.")
                continue

    tournament_stakes_list_dec = sorted(all_buyins_map.keys())
    all_buyins_str = [all_buyins_map[d] for d in tournament_stakes_list_dec]
    recommended_tournament_stake = "N/A"
    stake_explanation = ""
    next_stake_level = ""
    next_stake_message = ""
    move_down_message = ""
    move_down_stake_level = ""

    recommended_buy_in = Decimal('0.0')
    if mean_buy_ins > 0:
        recommended_buy_in = total_bankroll / mean_buy_ins

        # Find the recommended tournament stake
        found_stake_index = -1
        for i in range(len(tournament_stakes_list_dec) - 1, -1, -1):
            stake_dec = tournament_stakes_list_dec[i]
            if stake_dec <= recommended_buy_in:
                found_stake_index = i
                break
        
        if found_stake_index != -1:
            current_stake_dec = tournament_stakes_list_dec[found_stake_index]
            recommended_tournament_stake = all_buyins_str[found_stake_index]
            
            num_buy_ins_for_stake = total_bankroll / current_stake_dec if current_stake_dec > 0 else Decimal('inf')
            
            stake_explanation = (
                f"Based on your bankroll of ${total_bankroll:.2f} and the recommended {mean_buy_ins:.0f} buy-in rule, "
                f"your average buy-in should be ${recommended_buy_in:.2f}. The closest standard buy-in you can play is "
                f"{recommended_tournament_stake}, for which you have {num_buy_ins_for_stake:.1f} buy-ins."
            )

            # Move up logic
            if found_stake_index < len(all_buyins_str) - 1:
                next_stake_dec = tournament_stakes_list_dec[found_stake_index + 1]
                next_stake_level = all_buyins_str[found_stake_index + 1]
                required_bankroll_for_next_stake = next_stake_dec * mean_buy_ins
                additional_bankroll_needed = required_bankroll_for_next_stake - total_bankroll
                
                if additional_bankroll_needed > 0:
                    next_stake_message = (
                        f"To move up to {next_stake_level} tournaments, you need to win an additional "
                        f"${additional_bankroll_needed:.2f} to reach a bankroll of ${required_bankroll_for_next_stake:.2f}."
                    )

            # Move down logic
            if found_stake_index > 0:
                move_down_stake_dec = tournament_stakes_list_dec[found_stake_index - 1]
                move_down_stake_level = all_buyins_str[found_stake_index - 1]
                move_down_stake_required_br = move_down_stake_dec * mean_buy_ins
                amount_can_lose = total_bankroll - move_down_stake_required_br
                
                if amount_can_lose > 0:
                    move_down_message = (
                        f"You will need to move down to {move_down_stake_level} tournaments if you lose "
                        f"${amount_can_lose:.2f} to drop to a bankroll of ${move_down_stake_required_br:.2f}."
                    )
        else:
            recommended_tournament_stake = "Below Smallest Stakes"
            stake_explanation = (
                f"Your bankroll of ${total_bankroll:.2f} is too small for the lowest available stakes based on the "
                f"recommended {mean_buy_ins:.0f} buy-in rule. Your average buy-in should be ${recommended_buy_in:.2f}."
            )
            next_stake_level = all_buyins_str[0]
    else:
        stake_explanation = "Please make selections above to get a stake recommendation."

    return render_template('tournament_stakes.html',
                           total_bankroll=total_bankroll,
                           game_type=request.args.get('game_type', 'nlhe'),
                           skill_level=request.args.get('skill_level', 'tough'),
                           risk_tolerance=request.args.get('risk_tolerance', 'conservative'),
                           game_environment=request.args.get('game_environment', 'online'),
                           tournament_bankroll_recommendation=tournament_bankroll_recommendation,
                           recommended_buy_in=recommended_buy_in,
                           recommended_tournament_stake=recommended_tournament_stake,
                           stake_explanation=stake_explanation,
                           next_stake_level=next_stake_level,
                           next_stake_message=next_stake_message,
                           move_down_stake_level=move_down_stake_level,
                           move_down_message=move_down_message,
                           site_filter=request.args.get('site_filter', 'all'),
                           tournament_buy_ins=tournament_buy_ins
                           )