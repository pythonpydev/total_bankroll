from collections import Counter
import csv

def evaluate_hand_strength(hand_string: str) -> tuple[int, str, list, float]:
    """
    Evaluates a PLO hand string and assigns it to a tier based on heuristics
    point-based heuristic system. Returns tier, reason, score breakdown, and total score.
    """
    # 1. Parse hand into ranks and suits
    ranks_str = "23456789TJQKA"
    hand_string = hand_string.replace(" ", "")
    cards = [hand_string[i:i+2] for i in range(0, 8, 2)]
    ranks = sorted([ranks_str.index(c[0].upper()) for c in cards], reverse=True)
    suits = [card[1].lower() for c in cards]

    # 2. Determine hand properties
    rank_counts = Counter(ranks)
    suit_counts = Counter(suits)
    score = 0
    score_breakdown = []

    # --- 3. Score Calculation ---

    # a) Pair scoring (updated with tiered system)
    pairs = {rank: count for rank, count in rank_counts.items() if count == 2}
    trips = {rank: count for rank, count in rank_counts.items() if count == 3}
    quads = {rank: count for rank, count in rank_counts.items() if count == 4}

    # Handle trips/quads first (new addition)
    if quads:
        for rank in quads:
            points = round((rank + 1) * 10, 1)
            score += points
            rank_name = ranks_str[rank]
            score_breakdown.append((f"Quads of {rank_name}s", f"+{points}"))
    elif trips:
        for rank in trips:
            points = round((rank + 1) * 4, 1)
            score += points
            rank_name = ranks_str[rank]
            score_breakdown.append((f"Trips of {rank_name}s", f"+{points}"))

    # Pairs with tiered scoring
    if pairs:
        for rank in sorted(pairs, reverse=True):
            pair_rank_name = ranks_str[rank]
            if rank >= ranks_str.index('Q'):  # Premium: Q=10, K=11, A=12
                points = round((rank + 1) * 3.5 + 10, 1)
                tier = "Premium"
            elif rank >= ranks_str.index('7'):  # Mid: 7=5 to J=9 (T=8, J=9)
                points = round((rank + 1) * 2.5 + 5, 1)
                tier = "Mid"
            else:  # Low: <7 (0-4)
                points = round((rank + 1) * 1.5, 1)
                tier = "Low"
            
            # Check if pair is suited
            pair_indices = [i for i, r in enumerate(ranks) if r == rank][:2]  # First two if more
            suited_pair = suits[pair_indices[0]] == suits[pair_indices[1]] if len(pair_indices) == 2 else False
            if suited_pair:
                points += 5
                score_breakdown.append((f"Suited {tier} Pair of {pair_rank_name}s", f"+{points}"))
            else:
                score_breakdown.append((f"{tier} Pair of {pair_rank_name}s", f"+{points}"))
            
            score += points
        
        # Two Pair Bonus
        if len(pairs) == 2:
            bonus = 10
            pair_ranks = list(pairs.keys())
            if all(r >= ranks_str.index('7') for r in pair_ranks):
                bonus += 5
                score_breakdown.append(("High/Mid Two Pair Bonus", f"+{bonus}"))
            else:
                score_breakdown.append(("Two Pair Bonus", f"+{bonus}"))
            score += bonus

    # b) Suitedness scoring
    is_double_suited = list(suit_counts.values()).count(2) == 2
    is_single_suited = max(suit_counts.values()) >= 2  # Simplified: any suit with 2+

    suited_ranks = {}
    for i, suit in enumerate(suits):
        if suit not in suited_ranks: suited_ranks[suit] = []
        suited_ranks[suit].append(ranks[i])

    if is_double_suited:
        score += 25
        score_breakdown.append(("Double-Suited", "+25"))
        # Nut suit bonus
        for suit_ranks in suited_ranks.values():
            if len(suit_ranks) >= 2 and max(ranks_str.index('A'), *suit_ranks) == ranks_str.index('A'):
                score += 10
                score_breakdown.append(("Nut Suit Bonus", "+10"))
                break
    elif is_single_suited:
        score += 10
        score_breakdown.append(("Single-Suited", "+10"))
        # Nut suit bonus
        suited_suit = max(suit_counts, key=suit_counts.get)
        ace_rank = ranks_str.index('A')
        if ace_rank in ranks and suits[ranks.index(ace_rank)] == suited_suit:
            score += 5
            score_breakdown.append(("Nut Suit Bonus", "+5"))

    # Rainbow penalty (new)
    if max(suit_counts.values()) == 1:
        score -= 10
        score_breakdown.append(("Rainbow Penalty", "-10"))

    # c) Connectivity scoring (updated to subset-aware)
    # Find max streak of consecutive ranks
    max_streak = 1
    current_streak = 1
    is_broadway_streak = False
    for i in range(1, len(ranks)):
        if ranks[i-1] - ranks[i] == 1:
            current_streak += 1
            if ranks[i-1] >= ranks_str.index('T'):
                is_broadway_streak = True
        else:
            max_streak = max(max_streak, current_streak)
            current_streak = 1
            is_broadway_streak = False
    max_streak = max(max_streak, current_streak)

    if max_streak == 4:
        score += 25
        score_breakdown.append(("Full Rundown (4-card streak)", "+25"))
    elif max_streak == 3:
        score += 15
        score_breakdown.append(("Strong Partial Rundown (3-card streak)", "+15"))
    elif max_streak == 2:
        score += 5
        score_breakdown.append(("Basic Connectors (2-card streak)", "+5"))

    if is_broadway_streak and max_streak >= 2:
        score += 5
        score_breakdown.append(("Broadway Streak Bonus", "+5"))

    # Wheel bonus (new)
    ace_rank = ranks_str.index('A')
    low_ranks = [r for r in ranks if r <= ranks_str.index('5')]  # 2-5
    if ace_rank in ranks and len(low_ranks) >= 2:
        bonus = 5 * len(low_ranks)
        score += bonus
        score_breakdown.append((f"Wheel Potential ({len(low_ranks)+1} low cards w/ A)", f"+{bonus}"))

    # d) Suited connector bonuses (new)
    for suit, suit_ranks_list in suited_ranks.items():
        if len(suit_ranks_list) >= 2:
            suit_ranks_sorted = sorted(suit_ranks_list, reverse=True)
            for j in range(1, len(suit_ranks_sorted)):
                diff = suit_ranks_sorted[j-1] - suit_ranks_sorted[j]
                if diff <= 2:  # Connected or 1-gap
                    points = 5 if diff == 1 else 3
                    score += points
                    score_breakdown.append((f"Suited Connector/Gapper in {suit.upper()}", f"+{points}"))
                    if ace_rank in suit_ranks_sorted:
                        score += 3
                        score_breakdown.append(("Nut Suited Connector Bonus", "+3"))
                    # Cap per suit to avoid overcounting
                    break

    # e) High-card / Broadway scoring (adjusted)
    broadway_cards = [r for r in ranks if r >= ranks_str.index('T')]
    if broadway_cards:
        points = len(broadway_cards) * 5  # Increased from 4
        score += points
        score_breakdown.append((f"{len(broadway_cards)} Broadway Card(s)", f"+{points}"))
    if len(broadway_cards) == 4:
        score += 15
        score_breakdown.append(("All Broadway Bonus", "+15"))

    # f) Refined dangler penalties (new)
    danglers = 0
    for i in range(len(ranks)):
        # Check distance to nearest neighbors
        neighbors = [abs(ranks[i] - ranks[j]) for j in range(len(ranks)) if i != j]
        min_dist = min(neighbors) if neighbors else 99
        if min_dist > 3:
            danglers += 1
    if danglers > 0:
        penalty = danglers * 5
        if len(broadway_cards) >= 3 or is_double_suited:
            penalty /= 2  # Halve if strong elsewhere
        penalty = round(penalty, 1)
        score -= penalty
        score_breakdown.append((f"Dangler Penalty ({danglers} isolated cards)", f"-{penalty}"))

    # g) Blocker bonus (new, e.g., for AA)
    if rank_counts[ranks_str.index('A')] >= 2:
        score += 5
        score_breakdown.append(("Ace Blocker Bonus", "+5"))

    # --- 4. Tier Assignment (adjusted thresholds) ---
    if score >= 80:
        return 1, "Elite - A top-tier hand with immense nut potential, combining high pairs, suitedness, and connectivity.", score_breakdown, score
    elif score >= 65:
        return 2, "Premium - A very strong hand with excellent coordination, often featuring suited high pairs or powerful rundowns.", score_breakdown, score
    elif score >= 45:
        return 3, "Strong - A solid, profitable hand with good suited and/or connected components. Playable in most positions.", score_breakdown, score
    elif score >= 25:
        return 4, "Playable - A speculative hand that relies on position and hitting a favorable flop. Best played in late position or multi-way pots.", score_breakdown, score
    else:
        return 5, "Trash/Marginal - A weak hand with poor coordination. Lacks significant pair, suit, or straight potential and should usually be folded.", score_breakdown, score

if __name__ == "__main__":
    input_file = "plo_hands.csv"
    output_file = "plo_hands_evaluated.csv"

    with open(input_file, mode='r', newline='') as infile:
        reader = csv.reader(infile)
        headers = next(reader)  # Read headers: cards,strength,rating

        with open(output_file, mode='w', newline='') as outfile:
            writer = csv.writer(outfile)
            writer.writerow(headers)

            for row in reader:
                if row:  # Skip empty rows
                    hand = row[0]
                    tier, reason, breakdown, score = evaluate_hand_strength(hand)
                    row[1] = str(tier)  # strength = tier
                    row[2] = str(score)  # rating = score
                    writer.writerow(row)

    print(f"Processed {input_file} and wrote results to {output_file}")