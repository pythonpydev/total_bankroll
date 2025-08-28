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
        else:
            # This case should ideally not be reached if the loop covers all stakes
            recommended_stake = "N/A"
            stake_explanation = "Could not determine recommended stakes. Please check bankroll data."

    return render_template(
        'poker_stakes.html',
        total_bankroll=total_bankroll,
        cash_stakes_table=cash_stakes_table,
        recommended_stake=recommended_stake,
        stake_explanation=stake_explanation
    )