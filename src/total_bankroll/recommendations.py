import os
import json
from decimal import Decimal
from flask import current_app

def _format_stake_string(stake_row):
    """Helper to create a consistent stake string like '0.50/1.00'."""
    sb = Decimal(str(stake_row['small_blind']).replace('$', '').replace(',', ''))
    bb = Decimal(str(stake_row['big_blind']).replace('$', '').replace(',', ''))
    return f"{sb:.2f}/{bb:.2f}"
class RecommendationEngine:
    def __init__(self):
        config_path = os.path.join(current_app.root_path, 'data', 'recommendation_logic.json')
        with open(config_path, 'r') as f:
            self.config = json.load(f)

    def _calculate_weighted_range(self, selections, game_mode):
        """Generic function to calculate a weighted bankroll range."""
        mode_config = self.config[game_mode]
        weights = self.config['weights']
        
        total_weight = 0
        weighted_low_sum = 0
        weighted_high_sum = 0

        for key, selection in selections.items():
            if selection != "NA":
                weight = weights.get(key, 0)
                low, high = mode_config['ranges'].get(key, {}).get(selection, (0, 0))
                
                total_weight += weight
                weighted_low_sum += low * weight
                weighted_high_sum += high * weight

        if total_weight > 0:
            avg_low = round(weighted_low_sum / total_weight)
            avg_high = round(weighted_high_sum / total_weight)
            avg_multiple = (Decimal(avg_low) + Decimal(avg_high)) / Decimal('2.0')
        else:
            avg_low, avg_high, avg_multiple = 0, 0, Decimal('0.0')

        return {
            "low": avg_low,
            "high": avg_high,
            "average_multiple": avg_multiple,
            "unit": mode_config['unit'],
            "recommendation_string": f"{avg_low} to {avg_high} {mode_config['unit']}"
        }

    def get_cash_game_recommendation_data(self, selections, total_bankroll, cash_stakes_list):
        """
        Calculates all recommendation data for cash games.
        Returns a dictionary with recommendation data and formatted messages.
        """
        range_data = self._calculate_weighted_range(selections, 'cash_games')
        buy_in_multiple = range_data['average_multiple']
        
        recs = {
            "recommended_stake": "N/A",
            "stake_explanation": "Please make selections above to get a stake recommendation.",
            "next_stake_level": "",
            "next_stake_message": "",
            "move_down_stake_level": "",
            "move_down_message": "",
            "recommended_stake_index": -1
        }

        if buy_in_multiple <= 0:
            return recs

        # Find recommended stake
        for i in range(len(cash_stakes_list) - 1, -1, -1):
            stake_row = cash_stakes_list[i]
            max_buy_in = Decimal(str(stake_row['max_buy_in']).replace('$', '').replace(',', ''))
            if total_bankroll >= buy_in_multiple * max_buy_in:
                recs["recommended_stake"] = _format_stake_string(stake_row)
                recs["stake_explanation"] = (
                    f"Based on your bankroll of ${total_bankroll:.2f}, you have {total_bankroll / max_buy_in:.1f} "
                    f"buy-ins for {stake_row['small_blind']}/{stake_row['big_blind']} stakes. With the recommended {buy_in_multiple:.0f} "
                    f"buy-in rule, you can comfortably play at these stakes."
                )
                recs["recommended_stake_index"] = i
                break # Found the highest playable stake, so we stop.

        # Handle case where bankroll is below the smallest stake
        if recs["recommended_stake_index"] == -1 and cash_stakes_list:
            smallest_stake_row = cash_stakes_list[0]
            min_buy_in = Decimal(str(smallest_stake_row['min_buy_in']).replace('$', '').replace(',', ''))
            if total_bankroll < buy_in_multiple * min_buy_in:
                recs["recommended_stake"] = "Below Smallest Stakes"
                recs["stake_explanation"] = (
                    f"Your bankroll of ${total_bankroll:.2f} is less than {buy_in_multiple:.0f} times the minimum buy-in "
                    f"for the smallest available stakes ({smallest_stake_row['small_blind']}/{smallest_stake_row['big_blind']}). "
                    f"Consider depositing more funds to comfortably play at these stakes."
                )
                recs["next_stake_level"] = _format_stake_string(smallest_stake_row)

        if recs["recommended_stake_index"] == -1:
            return recs

        # Calculate "move up" message
        if recs["recommended_stake_index"] < len(cash_stakes_list) - 1:
            next_stake_row = cash_stakes_list[recs["recommended_stake_index"] + 1]
            recs["next_stake_level"] = _format_stake_string(next_stake_row)
            next_max_buy_in = Decimal(str(next_stake_row['max_buy_in']).replace('$', '').replace(',', ''))
            required_bankroll = buy_in_multiple * next_max_buy_in
            additional_needed = required_bankroll - total_bankroll
            if additional_needed > 0:
                recs["next_stake_message"] = (
                    f"To move up to {recs['next_stake_level']} stakes, you need to win an additional "
                    f"${additional_needed:.2f} to reach a bankroll of ${required_bankroll:.2f}."
                )

        # Calculate "move down" message
        if recs["recommended_stake_index"] > 0:
            # The "move down" stake is the one below the current recommended one.
            recs["move_down_stake_level"] = _format_stake_string(cash_stakes_list[recs["recommended_stake_index"] - 1])
            
            current_stake_row = cash_stakes_list[recs["recommended_stake_index"]]
            current_min_buy_in = Decimal(str(current_stake_row['min_buy_in']).replace('$', '').replace(',', ''))
            move_down_threshold = buy_in_multiple * current_min_buy_in
            amount_can_lose = total_bankroll - move_down_threshold

            if amount_can_lose >= 0:
                recs["move_down_message"] = (
                    f"You will need to move down to {recs['move_down_stake_level']} stakes if you lose "
                    f"${amount_can_lose:.2f} to drop to a bankroll of ${move_down_threshold:.2f}."
                )
        
        return recs

    def get_tournament_recommendation_data(self, selections, total_bankroll, tournament_stakes_map):
        """
        Calculates all recommendation data for tournaments.
        `tournament_stakes_map` is a dict of {Decimal(buy_in): "str_buy_in"}
        """
        range_data = self._calculate_weighted_range(selections, 'tournaments')
        mean_buy_ins = range_data['average_multiple']

        recs = {
            "recommended_tournament_stake": "N/A",
            "stake_explanation": "Please make selections above to get a stake recommendation.",
            "next_stake_level": "",
            "next_stake_message": "",
            "move_down_stake_level": "",
            "move_down_message": "",
            "recommended_buy_in": Decimal('0.0'),
            "recommended_tournament_stake_dec": None,
            "next_stake_level_dec": None,
            "move_down_stake_level_dec": None,
        }

        if mean_buy_ins <= 0:
            return recs

        recs["recommended_buy_in"] = total_bankroll / mean_buy_ins
        
        sorted_stakes_dec = sorted(tournament_stakes_map.keys())

        # Find the recommended tournament stake
        found_stake_index = -1
        for i in range(len(sorted_stakes_dec) - 1, -1, -1):
            if sorted_stakes_dec[i] <= recs["recommended_buy_in"]:
                found_stake_index = i
                break
        
        if found_stake_index != -1:
            current_stake_dec = sorted_stakes_dec[found_stake_index]
            recs["recommended_tournament_stake"] = tournament_stakes_map[current_stake_dec]
            recs["recommended_tournament_stake_dec"] = current_stake_dec
            
            num_buy_ins_for_stake = total_bankroll / current_stake_dec if current_stake_dec > 0 else Decimal('inf')
            
            recs["stake_explanation"] = (
                f"Based on your bankroll of ${total_bankroll:.2f} and the recommended {mean_buy_ins:.0f} buy-in rule, "
                f"your average buy-in should be ${recs['recommended_buy_in']:.2f}. The closest standard buy-in you can play is "
                f"{recs['recommended_tournament_stake']}, for which you have {num_buy_ins_for_stake:.1f} buy-ins."
            )

            # Move up logic
            if found_stake_index < len(sorted_stakes_dec) - 1:
                next_stake_dec = sorted_stakes_dec[found_stake_index + 1]
                recs["next_stake_level"] = tournament_stakes_map[next_stake_dec]
                recs["next_stake_level_dec"] = next_stake_dec
                required_bankroll = next_stake_dec * mean_buy_ins
                additional_needed = required_bankroll - total_bankroll

                if additional_needed > 0:
                    recs["next_stake_message"] = f"To move up to {recs['next_stake_level']} tournaments, you need to win or deposit an additional ${additional_needed:.2f} to reach a bankroll of ${required_bankroll:.2f}."
                else:
                    recs["next_stake_message"] = f"You are already sufficiently rolled to start playing at {recs['next_stake_level']} tournaments."

            # Move down logic
            if found_stake_index > 0:
                move_down_stake_dec = sorted_stakes_dec[found_stake_index - 1]
                recs["move_down_stake_level"] = tournament_stakes_map[move_down_stake_dec]
                recs["move_down_stake_level_dec"] = move_down_stake_dec
                required_bankroll = current_stake_dec * mean_buy_ins
                amount_can_lose = total_bankroll - required_bankroll
                recs["move_down_message"] = f"You will need to move down to {recs['move_down_stake_level']} tournaments if you lose ${amount_can_lose:.2f} to drop to a bankroll of ${required_bankroll:.2f}."
        else: # Below smallest stakes
            recs["recommended_tournament_stake"] = "Below Smallest Stakes"
            recs["stake_explanation"] = f"Your bankroll of ${total_bankroll:.2f} is too small for the lowest available stakes based on the recommended {mean_buy_ins:.0f} buy-in rule. Your average buy-in should be ${recs['recommended_buy_in']:.2f}."
            if sorted_stakes_dec:
                next_stake_dec = sorted_stakes_dec[0]
                recs["next_stake_level"] = tournament_stakes_map[next_stake_dec]
                required_bankroll = next_stake_dec * mean_buy_ins
                additional_needed = required_bankroll - total_bankroll
                recs["next_stake_message"] = f"To play at the lowest stakes ({recs['next_stake_level']}), you need to win or deposit an additional ${additional_needed:.2f} to reach a bankroll of ${required_bankroll:.2f}."
                
        return recs