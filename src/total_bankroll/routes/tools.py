from flask import Blueprint, render_template
from flask_security import current_user
from decimal import Decimal
from ..utils import get_user_bankroll_data

tools_bp = Blueprint('tools', __name__)

@tools_bp.route('/tools')
def tools_page():
    return render_template('tools.html')

@tools_bp.route('/poker_stakes')
def poker_stakes_page():
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

    # Iterate through stakes from largest to smallest
    for i in range(len(cash_stakes_table) - 1, 0, -1):
        stake_row = cash_stakes_table[i]
        max_buy_in_str = stake_row[4]  # Maximum Buy-In is the 5th column (index 4)
        max_buy_in = parse_currency_to_decimal(max_buy_in_str)

        if total_bankroll >= 30 * max_buy_in:
            recommended_stake = f"{stake_row[1]}/{stake_row[2]}"
            stake_explanation = (
                f"Based on your bankroll of ${total_bankroll:.2f}, you have {total_bankroll / max_buy_in:.2f} "
                f"times the maximum buy-in for {stake_row[1]}/{stake_row[2]} stakes. "
                f"With the recommended 30x maximum buy-in rule, you can comfortably play at these stakes."
            )
            break
    else:
        # If no stake meets the condition, recommend the smallest stake or suggest depositing more
        smallest_stake_row = cash_stakes_table[1]
        smallest_min_buy_in = parse_currency_to_decimal(smallest_stake_row[3])
        if total_bankroll < 30 * smallest_min_buy_in:
            recommended_stake = "Below Smallest Stakes"
            stake_explanation = (
                f"Your bankroll of ${total_bankroll:.2f} is less than 30 times the minimum buy-in "
                f"for the smallest available stakes ({smallest_stake_row[1]}/{smallest_stake_row[2]}). "
                f"Consider depositing more funds to comfortably play at these stakes."
            )
            next_stake_level = f"{smallest_stake_row[1]}/{smallest_stake_row[2]}"
        else:
            # This case should ideally not be reached if the loop covers all stakes
            recommended_stake = "N/A"
            stake_explanation = "Could not determine recommended stakes. Please check bankroll data."

    # Calculate next stake message
    next_stake_message = ""
    if recommended_stake != "N/A" and recommended_stake != "Below Smallest Stakes":
        # Find the index of the recommended stake
        recommended_stake_index = -1
        for i, row in enumerate(cash_stakes_table):
            if i > 0 and f"{row[1]}/{row[2]}" == recommended_stake:
                recommended_stake_index = i
                break
        print(f"Recommended Stake Index: {recommended_stake_index}")

        if recommended_stake_index != -1 and recommended_stake_index < len(cash_stakes_table) - 1:
            print("Inside next_stake_level assignment block.")
            next_stake_row = cash_stakes_table[recommended_stake_index + 1]
            next_stake_sb = next_stake_row[1]
            next_stake_bb = next_stake_row[2]
            next_stake_level = f"{next_stake_sb}/{next_stake_bb}"
            next_stake_max_buy_in = parse_currency_to_decimal(next_stake_row[4])
            
            required_bankroll_for_next_stake = 30 * next_stake_max_buy_in
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
    move_down_message = ""
    move_down_stake_level = ""

    # Get smallest stake max buy-in for comparison
    smallest_stake_row = cash_stakes_table[1]
    smallest_max_buy_in_for_check = parse_currency_to_decimal(smallest_stake_row[4])

    if total_bankroll <= 30 * smallest_max_buy_in_for_check:
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
            
            # The threshold to move down is 30x the max buy-in of the *lower* stake
            move_down_threshold_max_buy_in = parse_currency_to_decimal(move_down_stake_row[4])
            required_bankroll_to_stay_at_current_stake = 30 * move_down_threshold_max_buy_in
            
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

    return render_template(
        'poker_stakes.html',
        total_bankroll=total_bankroll,
        cash_stakes_table=cash_stakes_table,
        recommended_stake=recommended_stake,
        stake_explanation=stake_explanation,
        next_stake_message=next_stake_message,
        next_stake_level=next_stake_level,
        move_down_message=move_down_message,
        move_down_stake_level=move_down_stake_level
    )