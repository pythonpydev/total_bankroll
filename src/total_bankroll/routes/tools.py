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

@tools_bp.route('/poker_stakes')
@login_required
def poker_stakes_page():
    # Get filter values from request, with defaults
    game_type = request.args.get('game_type', 'nlhe')
    skill_level = request.args.get('skill_level', 'tough')
    risk_tolerance = request.args.get('risk_tolerance', 'conservative')
    game_environment = request.args.get('game_environment', 'online')

    site_filter = request.args.get('site_filter', 'all')
    # Map form values to display values for the algorithm
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

    # Calculate the bankroll recommendation based on selections
    bankroll_recommendation = calculate_bankroll_range(
        game_type_map.get(game_type), skill_level_map.get(skill_level), 
        risk_tolerance_map.get(risk_tolerance), game_environment_map.get(game_environment)
    )

    # Parse the bankroll recommendation to get the mean buy-in multiple
    buy_in_multiple = Decimal('30.0')  # Default value
    try:
        # e.g., "44 to 86 big blinds"
        parts = bankroll_recommendation.split()
        low = int(parts[0])
        high = int(parts[2])
        if high > 0:
            buy_in_multiple = (Decimal(low) + Decimal(high)) / Decimal('2.0')
        else:
            # "0 to 0" means not applicable.
            buy_in_multiple = Decimal('0.0')
    except (ValueError, IndexError):
        buy_in_multiple = Decimal('30.0')

    bankroll_data = get_user_bankroll_data(current_user.id)
    total_bankroll = bankroll_data['total_bankroll']

    cash_stakes_table = [
        ["ID", "Small Blind", "Big Blind", "Minimum Buy-In", "Maximum Buy-In"],
        [1, "$0.01", "$0.02", "$0.80", "$2.00"],
        [2, "$0.02", "$0.05", "$2.00", "$5.00"],
        [3, "$0.05", "$0.10", "$4.00", "$10.00"],
        [4, "$0.10", "$0.25", "$10.00", "$25.00"],
        [5, "$0.25", "$0.50", "$20.00", "$50.00"],
        [6, "$0.50", "$1.00", "$40.00", "$100.00"],
        [7, "$1.00", "$2.00", "$80.00", "$200.00"],
        [8, "$2.00", "$5.00", "$200.00", "$500.00"],
        [9, "$5.00", "$10.00", "$400.00", "$1,000.00"],
        [10, "$10.00", "$20.00", "$800.00", "$2,000.00"],
        [11, "$25.00", "$50.00", "$2,000.00", "$5,000.00"],
        [12, "$50.00", "$100.00", "$4,000.00", "$10,000.00"],
        [13, "$100.00", "$200.00", "$8,000.00", "$20,000.00"],
    ]

    # Function to parse currency string to Decimal
    def parse_currency_to_decimal(currency_str):
        return Decimal(currency_str.replace('$', '').replace(',', ''))

    recommended_stake = "N/A"
    stake_explanation = ""
    next_stake_level = ""
    next_stake_message = ""
    move_down_message = ""
    move_down_stake_level = ""

    if buy_in_multiple > 0:
        # Iterate through stakes from largest to smallest
        for i in range(len(cash_stakes_table) - 1, 0, -1):
            stake_row = cash_stakes_table[i]
            max_buy_in_str = stake_row[4]  # Maximum Buy-In is the 5th column (index 4)
            max_buy_in = parse_currency_to_decimal(max_buy_in_str)

            if total_bankroll >= buy_in_multiple * max_buy_in:
                recommended_stake = f"{stake_row[1]}/{stake_row[2]}"
                stake_explanation = (
                    f"Based on your bankroll of ${total_bankroll:.2f}, you have {total_bankroll / max_buy_in:.1f} "
                    f"buy-ins for {stake_row[1]}/{stake_row[2]} stakes. With the recommended {buy_in_multiple:.0f} "
                    f"buy-in rule, you can comfortably play at these stakes."
                )
                break
        else:
            # If no stake meets the condition, recommend the smallest stake or suggest depositing more
            smallest_stake_row = cash_stakes_table[1]
            smallest_min_buy_in = parse_currency_to_decimal(smallest_stake_row[3])
            if total_bankroll < buy_in_multiple * smallest_min_buy_in:
                recommended_stake = "Below Smallest Stakes"
                stake_explanation = (
                    f"Your bankroll of ${total_bankroll:.2f} is less than {buy_in_multiple:.0f} times the minimum buy-in "
                    f"for the smallest available stakes ({smallest_stake_row[1]}/{smallest_stake_row[2]}). "
                    f"Consider depositing more funds to comfortably play at these stakes."
                )
                next_stake_level = f"{smallest_stake_row[1]}/{smallest_stake_row[2]}"
            else:
                # This case should ideally not be reached if the loop covers all stakes
                recommended_stake = "N/A"
                stake_explanation = "Could not determine recommended stakes. Please check bankroll data."

        # Calculate next stake message
        if recommended_stake != "N/A" and recommended_stake != "Below Smallest Stakes":
            # Find the index of the recommended stake
            recommended_stake_index = -1
            for i, row in enumerate(cash_stakes_table):
                if i > 0 and f"{row[1]}/{row[2]}" == recommended_stake:
                    recommended_stake_index = i
                    break

            if recommended_stake_index != -1 and recommended_stake_index < len(cash_stakes_table) - 1:
                next_stake_row = cash_stakes_table[recommended_stake_index + 1]
                next_stake_sb = next_stake_row[1]
                next_stake_bb = next_stake_row[2]
                next_stake_level = f"{next_stake_sb}/{next_stake_bb}"
                next_stake_max_buy_in = parse_currency_to_decimal(next_stake_row[4])
                
                required_bankroll_for_next_stake = buy_in_multiple * next_stake_max_buy_in
                additional_bankroll_needed = required_bankroll_for_next_stake - total_bankroll

                if additional_bankroll_needed > 0:
                    next_stake_message = (
                        f"To move up to {next_stake_sb}/{next_stake_bb} stakes, you need to win an additional "
                        f"${additional_bankroll_needed:.2f} to reach a bankroll of ${required_bankroll_for_next_stake:.2f}."
                    )
                else:
                    next_stake_message = (
                        f"You have enough bankroll to play at {next_stake_sb}/{next_stake_bb} stakes or higher!"
                    )
        # Calculate move down message
        # Get smallest stake max buy-in for comparison
        smallest_stake_row = cash_stakes_table[1]
        smallest_max_buy_in_for_check = parse_currency_to_decimal(smallest_stake_row[4])

        if total_bankroll <= buy_in_multiple * smallest_max_buy_in_for_check:
            move_down_message = ""
            move_down_stake_level = ""
        elif recommended_stake != "N/A" and recommended_stake != "Below Smallest Stakes":
            # Find the index of the recommended stake
            recommended_stake_index = -1
            for i, row in enumerate(cash_stakes_table):
                if i > 0 and f"{row[1]}/{row[2]}" == recommended_stake:
                    recommended_stake_index = i
                    break

            if recommended_stake_index > 1: # Ensure there's a stake to move down to
                move_down_stake_row = cash_stakes_table[recommended_stake_index - 1]
                move_down_sb = move_down_stake_row[1]
                move_down_bb = move_down_stake_row[2]
                move_down_stake_level = f"{move_down_sb}/{move_down_bb}"
                
                # The threshold to move down is based on the max buy-in of the *lower* stake
                move_down_threshold_max_buy_in = parse_currency_to_decimal(move_down_stake_row[4])
                required_bankroll_to_stay_at_current_stake = buy_in_multiple * move_down_threshold_max_buy_in
                
                amount_can_lose = total_bankroll - required_bankroll_to_stay_at_current_stake

                if amount_can_lose < 0:
                    # This case means current bankroll is already below the threshold for the lower stake
                    # This should ideally be covered by recommended_stake logic, but as a safeguard
                    move_down_message = (
                        f"You are currently playing above your recommended stakes. "
                        f"You should move down to {move_down_sb}/{move_down_bb} stakes."
                    )
                else:
                    move_down_message = (
                        f"You will need to move down to {move_down_sb}/{move_down_bb} stakes if you lose "
                        f"${amount_can_lose:.2f} to drop to a bankroll of ${required_bankroll_to_stay_at_current_stake:.2f}."
                    )
    else:
        # This handles the case where buy_in_multiple is 0
        recommended_stake = "N/A"
        stake_explanation = "Please make selections above to get a stake recommendation."

    return render_template(
        'poker_stakes.html',
        total_bankroll=total_bankroll,
        cash_stakes_table=cash_stakes_table,
        recommended_stake=recommended_stake,
        stake_explanation=stake_explanation,
        next_stake_message=next_stake_message,
        next_stake_level=next_stake_level,
        move_down_message=move_down_message,
        move_down_stake_level=move_down_stake_level,
        bankroll_recommendation=bankroll_recommendation,
        # Pass filter values to template
        game_type=game_type,
        skill_level=skill_level,
        risk_tolerance=risk_tolerance,
        game_environment=game_environment
    )

@tools_bp.route('/tournament_stakes')
@login_required
def tournament_stakes_page():
    """Tournament Stakes page."""
    # Get filter values from request, with defaults
    game_type = request.args.get('game_type', 'nlhe')
    skill_level = request.args.get('skill_level', 'tough')
    risk_tolerance = request.args.get('risk_tolerance', 'conservative')
    game_environment = request.args.get('game_environment', 'online')

    site_filter = request.args.get('site_filter', 'all')

    # Load tournament buy-in data from JSON
    json_path = os.path.join(current_app.root_path, 'data', 'tournament_buy_ins.json')
    with open(json_path, 'r') as f:
        tournament_buy_ins = json.load(f)


    # Map form values to display values for the algorithm
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

    tournament_bankroll_recommendation = calculate_tournament_bankroll_range(
        game_type_map.get(game_type), skill_level_map.get(skill_level),
        risk_tolerance_map.get(risk_tolerance), game_environment_map.get(game_environment)
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
                           game_type=game_type,
                           skill_level=skill_level,
                           risk_tolerance=risk_tolerance,
                           game_environment=game_environment,
                           tournament_bankroll_recommendation=tournament_bankroll_recommendation,
                           recommended_buy_in=recommended_buy_in,
                           recommended_tournament_stake=recommended_tournament_stake,
                           stake_explanation=stake_explanation,
                           next_stake_level=next_stake_level,
                           next_stake_message=next_stake_message,
                           move_down_stake_level=move_down_stake_level,
                           move_down_message=move_down_message,
                           site_filter=site_filter,
                           tournament_buy_ins=tournament_buy_ins
                           )