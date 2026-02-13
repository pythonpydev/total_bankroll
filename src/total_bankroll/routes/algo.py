# /home/ed/Insync/e.f.bird@outlook.com/OneDrive/Dev/spr/src/spr/algo.py

import random
import itertools
from treys import Card, Evaluator, Deck

evaluator = Evaluator()

def calculate_spr(hero_stack, opponent_stack, pot_size, bet_size=0):
    """
    Calculates the Stack-to-Pot Ratio (SPR).
    """
    current_pot_after_bet = pot_size + bet_size
    if current_pot_after_bet <= 0:
        return None
    smallest_stack = min(hero_stack, opponent_stack)
    return smallest_stack / current_pot_after_bet

def calculate_pot_sized_bets(hero_stack, opponent_stack, pot_size, bet_size=0):
    """
    Calculates the number of pot-sized bets possible.
    This implementation correctly follows poker rules for pot-sized raises.
    """
    effective_stack = min(hero_stack, opponent_stack)
    
    current_stack = effective_stack
    current_pot = pot_size
    num_pot_sized_bets = 0

    if bet_size > 0:
        pot_sized_bet_amount = current_pot + bet_size
        if current_stack >= pot_sized_bet_amount:
            current_stack -= pot_sized_bet_amount
            current_pot += (pot_sized_bet_amount * 2)
            num_pot_sized_bets += 1
            
            while current_stack > 0 and current_pot > 0 and current_stack >= current_pot:
                bet = current_pot
                current_stack -= bet
                current_pot += (bet * 2)
                num_pot_sized_bets += 1
    else:  # No bet facing
        while current_stack > 0 and current_pot > 0 and current_stack >= current_pot:
            bet = current_pot
            current_stack -= bet
            current_pot += (bet * 2)
            num_pot_sized_bets += 1
            
    return num_pot_sized_bets

def _get_best_plo_rank(hole, board):
    print(f"_get_best_plo_rank called with: hole={hole}, board={board}")
    if len(hole) != 4 or len(board) < 3:
        print("  Invalid hand or board length for PLO.")
        return float('inf')
    
    best_rank = float('inf')
    hole_treys = [Card.new(c) for c in hole]
    board_treys = [Card.new(c) for c in board]

    for hole_combo in itertools.combinations(hole_treys, 2):
        for board_combo in itertools.combinations(board_treys, 3):
            hand = list(hole_combo) + list(board_combo)
            try:
                rank = evaluator.evaluate(hand, [])
                # Debugging specific hand: AcAdAsKh + AsKhQs
                if sorted([Card.int_to_str(c) for c in hand]) == sorted(['Ac', 'Ad', 'As', 'Kh', 'Qs']):
                    print(f"  *** Debugging specific hand: {[Card.int_to_str(c) for c in hand]}, Rank: {rank}, Class: {evaluator.get_rank_class(rank)}")
                
                if rank < best_rank:
                    best_rank = rank
            except KeyError:
                continue
    print(f"_get_best_plo_rank returning: {best_rank}")
    return best_rank

def calculate_detailed_outs(hole_card_strs, board_card_strs):
    """
    Calculates the number of outs for a given PLO hand and board, categorized by hand type.
    This version correctly implements PLO hand evaluation rules and hand class mappings.
    """
    all_cards = hole_card_strs + board_card_strs
    if len(all_cards) != len(set(all_cards)):
        raise ValueError("Duplicate cards detected in hole cards or board cards.")
    current_best_rank = _get_best_plo_rank(hole_card_strs, board_card_strs)
    current_best_class = evaluator.get_rank_class(current_best_rank)

    outs_breakdown = {
        'pair': 0, 'two_pair': 0, 'trips': 0, 'straight': 0,
        'flush': 0, 'full_house': 0, 'quads': 0, 'straight_flush': 0, 'total': 0,
        'cards': []
    }

    deck = Deck()
    known_cards_treys = [Card.new(s) for s in hole_card_strs + board_card_strs]
    
    # Remove known cards from the deck to get available cards for simulation
    available_cards_treys = [c for c in deck.cards if c not in known_cards_treys]

    for potential_out_treys in available_cards_treys:
        potential_out_str = Card.int_to_str(potential_out_treys)
        simulated_board_strs = board_card_strs + [potential_out_str]
        
        simulated_best_rank = _get_best_plo_rank(hole_card_strs, simulated_board_strs)
        
        if simulated_best_rank < current_best_rank:
            print(f"Out card: {potential_out_str}")
            outs_breakdown['total'] += 1
            outs_breakdown['cards'].append(potential_out_str)
            simulated_best_class = evaluator.get_rank_class(simulated_best_rank)

            # Prioritize higher-ranking hands to avoid double-counting
            if simulated_best_class == 1: # Straight Flush
                outs_breakdown['straight_flush'] += 1
            elif simulated_best_class == 2: # Four of a Kind
                outs_breakdown['quads'] += 1
            elif simulated_best_class == 3: # Full House
                outs_breakdown['full_house'] += 1
            elif simulated_best_class == 4: # Flush
                # Only count as a flush out if current hand is not already a flush
                # or if it's a higher flush
                if current_best_class != 4 and current_best_class != 1: # Not already a flush or straight flush
                    outs_breakdown['flush'] += 1
                elif current_best_class == 4 and simulated_best_rank < current_best_rank: # Higher flush
                    outs_breakdown['flush'] += 1
            elif simulated_best_class == 5: # Straight
                # Only count as a straight out if current hand is not already a straight
                # or if it's a higher straight
                if current_best_class != 5 and current_best_class != 1: # Not already a straight or straight flush
                    outs_breakdown['straight'] += 1
                elif current_best_class == 5 and simulated_best_rank < current_best_rank: # Higher straight
                    outs_breakdown['straight'] += 1
            elif simulated_best_class == 6: # Three of a Kind
                outs_breakdown['trips'] += 1
            elif simulated_best_class == 7: # Two Pair
                outs_breakdown['two_pair'] += 1
            elif simulated_best_class == 8: # Pair
                outs_breakdown['pair'] += 1

    return outs_breakdown

def calculate_winning_outs(weaker_hand_cards, board_cards, stronger_hand_rank, all_known_cards):
    """
    Calculates the number of outs that will make the weaker hand win against the stronger hand's current rank.
    """
    winning_outs = {
        'total': 0,
        'cards': []
    }

    deck = Deck()
    known_cards_treys = [Card.new(s) for s in all_known_cards]
    
    # Get available cards for simulation
    available_cards_treys = [c for c in deck.cards if c not in known_cards_treys]

    for potential_out_treys in available_cards_treys:
        potential_out_str = Card.int_to_str(potential_out_treys)
        simulated_board_strs = board_cards + [potential_out_str]
        
        # Evaluate the weaker hand with the new board
        simulated_rank = _get_best_plo_rank(weaker_hand_cards, simulated_board_strs)
        
        # Check if the new rank is better than the stronger hand's current rank
        if simulated_rank < stronger_hand_rank:
            winning_outs['total'] += 1
            winning_outs['cards'].append(potential_out_str)
            
    return winning_outs

def run_improvement_simulation(hole_card_strs, board_card_strs, iterations=2000):
    """
    Runs a Monte Carlo simulation to calculate the probability of improving a hand
    and the probability of improving to specific hand types.
    """
    current_best_rank = _get_best_plo_rank(hole_card_strs, board_card_strs)

    all_known_cards = [Card.new(c) for c in hole_card_strs + board_card_strs]
    deck = Deck()
    unknown_cards = [c for c in deck.cards if c not in all_known_cards]
    cards_to_deal = 5 - len(board_card_strs)

    improvement_counts = {
        'total': 0, 'pair': 0, 'two_pair': 0, 'trips': 0, 'straight': 0,
        'flush': 0, 'full_house': 0, 'quads': 0, 'straight_flush': 0
    }

    if cards_to_deal <= 0:
        return {key: 0.0 for key in improvement_counts}

    for _ in range(iterations):
        random.shuffle(unknown_cards)
        sim_board_extension = unknown_cards[:cards_to_deal]
        sim_board = board_card_strs + [Card.int_to_str(c) for c in sim_board_extension]

        simulated_rank = _get_best_plo_rank(hole_card_strs, sim_board)

        if simulated_rank < current_best_rank:
            improvement_counts['total'] += 1
            simulated_class = evaluator.get_rank_class(simulated_rank)
            
            # Map rank class to our dictionary keys
            if simulated_class == 1: improvement_counts['straight_flush'] += 1
            elif simulated_class == 2: improvement_counts['quads'] += 1
            elif simulated_class == 3: improvement_counts['full_house'] += 1
            elif simulated_class == 4: improvement_counts['flush'] += 1
            elif simulated_class == 5: improvement_counts['straight'] += 1
            elif simulated_class == 6: improvement_counts['trips'] += 1
            elif simulated_class == 7: improvement_counts['two_pair'] += 1
            elif simulated_class == 8: improvement_counts['pair'] += 1

    # Convert counts to percentages
    improvement_equity = {
        key: (count / iterations) * 100 for key, count in improvement_counts.items()
    }
    # Rename 'total' to 'total_improvement_equity' for clarity
    improvement_equity['total_improvement_equity'] = improvement_equity.pop('total')

    return improvement_equity


def run_monte_carlo_simulation(hero_hand, opponent_hand, board_cards, iterations=2000):
    """
    Runs a Monte Carlo simulation to calculate hero's equity against a specific opponent hand.
    """
    hero_treys = [Card.new(c) for c in hero_hand]
    opponent_treys = [Card.new(c) for c in opponent_hand]
    board_treys = [Card.new(c) for c in board_cards]

    all_known_cards = hero_treys + opponent_treys + board_treys
    
    # Create a deck of unknown cards
    deck = Deck()
    unknown_cards = [c for c in deck.cards if c not in all_known_cards]

    cards_to_deal = 5 - len(board_cards)
    
    wins = 0
    ties = 0

    if cards_to_deal <= 0: # Board is complete, no simulation needed
        hero_rank = _get_best_plo_rank(hero_hand, board_cards)
        opp_rank = _get_best_plo_rank(opponent_hand, board_cards)
        if hero_rank < opp_rank: return 100.0
        if hero_rank == opp_rank: return 50.0
        return 0.0

    for _ in range(iterations):
        random.shuffle(unknown_cards)
        sim_board_extension = unknown_cards[:cards_to_deal]
        sim_board = board_cards + [Card.int_to_str(c) for c in sim_board_extension]

        hero_rank = _get_best_plo_rank(hero_hand, sim_board)
        opp_rank = _get_best_plo_rank(opponent_hand, sim_board)

        if hero_rank < opp_rank: wins += 1
        elif hero_rank == opp_rank: ties += 1

    return ((wins + (ties / 2)) / iterations) * 100

def find_best_five_card_hand(hole_cards, board_cards):
    """Finds the best 5-card hand in PLO, requiring 2 cards from the hole and 3 from the board."""
    best_rank = float('inf')
    best_hand_cards = []

    hole_treys = [Card.new(c) for c in hole_cards]
    board_treys = [Card.new(c) for c in board_cards]

    if len(hole_treys) != 4 or len(board_treys) < 3:
        return [] # Not a valid PLO scenario

    for hole_combo_treys in itertools.combinations(hole_treys, 2):
        for board_combo_treys in itertools.combinations(board_treys, 3):
            hand_treys = list(hole_combo_treys) + list(board_combo_treys)
            try:
                rank = evaluator.evaluate(hand_treys, [])
                if rank < best_rank:
                    best_rank = rank
                    # Convert back to string representation for the return value
                    best_hand_cards = [Card.int_to_str(c) for c in hand_treys]
            except KeyError:
                continue # Skip invalid hands
                
    return best_hand_cards

def process_hand_data(form_data, button_position):
    hero_hand_str = form_data['hero_hand']
    board_cards_str = form_data['board']
    opp_hand_str = form_data['opponent_hand']

    def normalize_card_string(card_str):
        if len(card_str) == 2:
            return card_str[0].upper() + card_str[1].lower()
        return card_str

    hero_hand_list = [normalize_card_string(hero_hand_str[i:i+2]) for i in range(0, len(hero_hand_str), 2)]
    board_cards_list = [normalize_card_string(board_cards_str[i:i+2]) for i in range(0, len(board_cards_str), 2)]
    opp_hand_list = [normalize_card_string(opp_hand_str[i:i+2]) for i in range(0, len(opp_hand_str), 2)]

    processed_data = {
        'small_blind': float(form_data['small_blind']),
        'big_blind': float(form_data['big_blind']),
        'hero_stack': float(form_data['hero_stack']),
        'hero_position': form_data['hero_position'],
        'button_position': button_position,
        'hero_hand': hero_hand_list,
        'board': board_cards_list,
        'opponent_stack': float(form_data['opponent_stack']),
        'opponent_position': form_data['opponent_position'],
        'opponent_hand': opp_hand_list,
        'pot_size': float(form_data['pot_size']),
        'bet_size': float(form_data.get('bet_size', 0))
    }

    hero_eval_rank = _get_best_plo_rank(hero_hand_list, board_cards_list)
    hero_hand_name = evaluator.class_to_string(evaluator.get_rank_class(hero_eval_rank))
    hero_best_hand = find_best_five_card_hand(hero_hand_list, board_cards_list)
    hero_current_rank_class = evaluator.get_rank_class(hero_eval_rank)
    processed_data['hero_eval'] = hero_eval_rank
    processed_data['hero_hand_name'] = hero_hand_name
    processed_data['hero_best_hand'] = hero_best_hand
    processed_data['hero_current_rank_class'] = hero_current_rank_class

    opp_eval_rank = _get_best_plo_rank(opp_hand_list, board_cards_list)
    opp_hand_name = evaluator.class_to_string(evaluator.get_rank_class(opp_eval_rank))
    opp_best_hand = find_best_five_card_hand(opp_hand_list, board_cards_list)
    opp_current_rank_class = evaluator.get_rank_class(opp_eval_rank)
    processed_data['opp_eval'] = opp_eval_rank
    processed_data['opp_hand_name'] = opp_hand_name
    processed_data['opp_best_hand'] = opp_best_hand
    processed_data['opp_current_rank_class'] = opp_current_rank_class

    hero_outs_breakdown = calculate_detailed_outs(hero_hand_list, board_cards_list)
    processed_data['hero_outs_breakdown'] = hero_outs_breakdown

    opp_outs_breakdown = calculate_detailed_outs(opp_hand_list, board_cards_list)
    processed_data['opp_outs_breakdown'] = opp_outs_breakdown

    # Calculate winning outs for the player who is behind
    all_known_cards = hero_hand_list + opp_hand_list + board_cards_list
    processed_data['hero_winning_outs'] = {'total': 0, 'cards': []}
    processed_data['opp_winning_outs'] = {'total': 0, 'cards': []}

    if hero_eval_rank > opp_eval_rank: # Hero is behind
        winning_outs = calculate_winning_outs(hero_hand_list, board_cards_list, opp_eval_rank, all_known_cards)
        processed_data['hero_winning_outs'] = winning_outs
    elif opp_eval_rank > hero_eval_rank: # Opponent is behind
        winning_outs = calculate_winning_outs(opp_hand_list, board_cards_list, hero_eval_rank, all_known_cards)
        processed_data['opp_winning_outs'] = winning_outs

    # Run Monte Carlo simulation for hero's equity
    hero_equity = run_monte_carlo_simulation(hero_hand_list, opp_hand_list, board_cards_list)
    processed_data['hero_equity'] = hero_equity

    # Run Monte Carlo simulation for hero's improvement equity
    hero_improvement_equity = run_improvement_simulation(hero_hand_list, board_cards_list)
    processed_data['hero_improvement_equity'] = hero_improvement_equity


    smallest_stack = min(processed_data['hero_stack'], processed_data['opponent_stack'])
    current_pot_after_bet = processed_data['pot_size'] + processed_data['bet_size']

    actual_spr = calculate_spr(processed_data['hero_stack'], processed_data['opponent_stack'], processed_data['pot_size'], processed_data['bet_size'])
    actual_pot_bets = calculate_pot_sized_bets(processed_data['hero_stack'], processed_data['opponent_stack'], processed_data['pot_size'], processed_data['bet_size'])

    processed_data['actual_spr'] = actual_spr
    processed_data['actual_pot_bets'] = actual_pot_bets
    processed_data['actual_spr_calculation_str'] = f"[{smallest_stack} / ({processed_data['pot_size']}+{processed_data['bet_size']})]"

    # Calculate required equity based on pot odds
    pot_size = processed_data['pot_size']
    bet_size = processed_data['bet_size']
    required_equity = 0
    if bet_size > 0:
        # Required Equity = Amount to Call / (Total Pot After Calling)
        total_pot_after_call = pot_size + bet_size + bet_size
        required_equity = (bet_size / total_pot_after_call) * 100 if total_pot_after_call > 0 else 0
    processed_data['required_equity'] = required_equity

    return processed_data
