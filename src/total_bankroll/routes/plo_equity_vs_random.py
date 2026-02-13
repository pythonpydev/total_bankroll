import random
from collections import Counter
from itertools import combinations

def plo_equity_vs_random(hand_str, trials=10000):
    # Map ranks and suits to internal values
    ranks_map = {"2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "T": 10, "J": 11, "Q": 12, "K": 13, "A": 14}
    suits_map = {"c": 0, "d": 1, "h": 2, "s": 3}

    # Parse the hand string into card IDs (0-51)
    hero_cards = []
    for i in range(0, len(hand_str), 2):
        rank_str = hand_str[i].upper()
        suit_str = hand_str[i + 1].lower()
        rank = ranks_map.get(rank_str)
        if rank is None:
            raise ValueError(f"Invalid rank: {rank_str}")
        suit = suits_map.get(suit_str)
        if suit is None:
            raise ValueError(f"Invalid suit: {suit_str}")
        rank_id = rank - 2  # 0=2, ..., 12=A
        card_id = rank_id * 4 + suit
        hero_cards.append(card_id)

    if len(hero_cards) != 4:
        raise ValueError("Hand must contain exactly 4 cards")

    # Create deck and remove hero's cards
    deck = list(range(52))
    for c in hero_cards:
        deck.remove(c)

    # Function to get a comparable rank tuple for a 5-card hand (higher tuple = stronger hand)
    def get_rank_tuple(five_cards):
        # Extract values (2-14) and suits (0-3)
        values = [(c // 4 + 2) for c in five_cards]
        suits = [c % 4 for c in five_cards]

        # Sort values descending
        sorted_values = sorted(values, reverse=True)

        # Frequency count
        count = Counter(values)
        counts = sorted(count.values(), reverse=True)
        ranked_ranks = sorted(count, key=lambda x: (count[x], x), reverse=True)

        # Detect wheel (A-5 straight)
        is_wheel = sorted_values == [14, 5, 4, 3, 2]

        # Determine hand type (higher number = stronger)
        if len(count) == 5:  # Possible straight/flush/high card
            is_flush_ = len(set(suits)) == 1
            is_straight_ = (sorted_values[0] - sorted_values[4] == 4) or is_wheel
            high = 5 if is_wheel else sorted_values[0]
            if is_flush_ and is_straight_:
                type_ = 8  # Straight flush
                tie = (high,)
            elif is_flush_:
                type_ = 5  # Flush
                tie = tuple(sorted_values)
            elif is_straight_:
                type_ = 4  # Straight
                tie = (high,)
            else:
                type_ = 0  # High card
                tie = tuple(sorted_values)
        elif len(count) == 4:
            type_ = 1  # One pair
            pair_rank = ranked_ranks[0]
            kickers = [v for v in sorted_values if v != pair_rank][:3]
            tie = (pair_rank,) + tuple(sorted(kickers, reverse=True))
        elif len(count) == 3:
            if counts[0] == 3:
                type_ = 3  # Three of a kind
                three_rank = ranked_ranks[0]
                kickers = [v for v in sorted_values if v != three_rank]
                tie = (three_rank,) + tuple(sorted(kickers, reverse=True))
            else:
                type_ = 2  # Two pair
                high_pair = max(ranked_ranks[0:2])
                low_pair = min(ranked_ranks[0:2])
                kicker = ranked_ranks[2]
                tie = (high_pair, low_pair, kicker)
        elif len(count) == 2:
            if counts[0] == 4:
                type_ = 7  # Four of a kind
                four_rank = ranked_ranks[0]
                kicker = ranked_ranks[1]
                tie = (four_rank, kicker)
            else:
                type_ = 6  # Full house
                three_rank = ranked_ranks[0] if count[ranked_ranks[0]] == 3 else ranked_ranks[1]
                pair_rank = ranked_ranks[1] if count[ranked_ranks[1]] == 2 else ranked_ranks[0]
                tie = (three_rank, pair_rank)
        else:
            type_ = 0  # Invalid/fallback
            tie = (0,)

        # Return tuple padded for comparison (higher better)
        return (type_,) + tie + (0, 0, 0, 0, 0)[len(tie):]

    # Evaluate best hand for Omaha (2 from hole + 3 from board)
    def evaluate_omaha(hole, board):
        best = (-1, 0, 0, 0, 0, 0, 0)  # Start low
        for h2 in combinations(hole, 2):
            for b3 in combinations(board, 3):
                five = list(h2) + list(b3)
                rank_tuple = get_rank_tuple(five)
                if rank_tuple > best:
                    best = rank_tuple
        return best

    # Monte Carlo simulation
    wins = 0
    ties = 0
    for _ in range(trials):
        random.shuffle(deck)
        opp = deck[0:4]
        board = deck[4:9]
        hero_rank = evaluate_omaha(hero_cards, board)
        opp_rank = evaluate_omaha(opp, board)
        if hero_rank > opp_rank:
            wins += 1
        elif hero_rank == opp_rank:
            ties += 1

    # Calculate equity
    equity = (wins + ties / 2) / trials * 100
    return equity

# Example usage:
# equity = plo_equity_vs_random("QhQd4s5c")
# print(f"Equity: {equity:.2f}%")
