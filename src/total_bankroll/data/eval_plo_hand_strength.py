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
    suits = [card[1].lower() for card in cards]

    # 2. Determine hand properties
    rank_counts = Counter(ranks)
    suit_counts = Counter(suits)
    score = 0
    score_breakdown = []

    # --- 3. Score Calculation ---

    # a) Pair scoring
    pairs = {rank: count for rank, count in rank_counts.items() if count == 2}
    if pairs:
        for rank in pairs:
            # Higher pairs are worth more
            points = round((rank + 1) * 2.5, 1)
            score += points
            pair_rank_name = ranks_str[rank]
            score_breakdown.append((f"Pair of {pair_rank_name}s", f"+{points}"))
        # Bonus for two pairs
        if len(pairs) == 2:
            score += 10
            score_breakdown.append(("Two Pair Bonus", "+10"))

    # b) Suitedness scoring
    is_double_suited = list(suit_counts.values()).count(2) == 2
    is_single_suited = 2 in suit_counts.values() or 3 in suit_counts.values()

    if is_double_suited:
        score += 25
        score_breakdown.append(("Double-Suited", "+25"))
        # Bonus if one of the suits is an Ace-high suit
        suited_ranks = {}
        for i, suit in enumerate(suits):
            if suit not in suited_ranks: suited_ranks[suit] = []
            suited_ranks[suit].append(ranks[i])
        for suit_ranks in suited_ranks.values():
            if len(suit_ranks) >= 2 and ranks_str.index('A') in suit_ranks:
                score += 10 # Nut suit bonus
                score_breakdown.append(("Nut Suit Bonus", "+10"))
                break
    elif is_single_suited:
        score += 10
        score_breakdown.append(("Single-Suited", "+10"))
        # Bonus for nut suit (check if an Ace is part of the suited cards)
        suited_suit = next((s for s, c in suit_counts.items() if c >= 2), None)
        ace_index_in_ranks = ranks.index(ranks_str.index('A')) if ranks_str.index('A') in ranks else -1
        if suited_suit and ace_index_in_ranks != -1 and suits[ace_index_in_ranks] == suited_suit:
            score += 5
            score_breakdown.append(("Nut Suit Bonus", "+5"))

    # c) Connectivity scoring
    gaps = [ranks[i] - ranks[i+1] - 1 for i in range(3)]
    total_gaps = sum(gaps)

    if total_gaps == 0: # 0-gap rundown (e.g., JT98)
        score += 25
        score_breakdown.append(("0-Gap Rundown", "+25"))
    elif total_gaps == 1: # 1-gap rundown (e.g., JT97)
        score += 18
        score_breakdown.append(("1-Gap Rundown", "+18"))
    elif total_gaps == 2: # 2-gap rundown (e.g., JT87)
        score += 12
        score_breakdown.append(("2-Gap Rundown", "+12"))
    elif total_gaps == 3:
        score += 5
        score_breakdown.append(("3-Gap Rundown", "+5"))

    # d) High-card / Broadway scoring
    broadway_cards = [r for r in ranks if r >= ranks_str.index('T')]

    # Penalize large gaps (danglers), but be less harsh if the other 3 cards are strong
    large_gaps = [g for g in gaps if g > 2]
    if len(large_gaps) > 0 and len(broadway_cards) < 3: # Only penalize if there's a dangler AND the hand isn't top-heavy
        penalty = min(sum(large_gaps) * 2, 15) # Scale penalty by gap size, capped at -15
        score -= penalty
        score_breakdown.append(("Large Gap(s) / Dangler", f"-{penalty}"))

    # d) High-card / Broadway scoring
    if broadway_cards:
        points = len(broadway_cards) * 4
        score += points
        score_breakdown.append((f"{len(broadway_cards)} Broadway Card(s)", f"+{points}"))
    if len(broadway_cards) == 4: # All broadway
        score += 15
        score_breakdown.append(("All Broadway Bonus", "+15"))

    # --- 4. Tier Assignment ---
    if score >= 85:
        return 1, "Elite - A top-tier hand with immense nut potential, combining high pairs, suitedness, and connectivity.", score_breakdown, score
    elif score >= 70:
        return 2, "Premium - A very strong hand with excellent coordination, often featuring suited high pairs or powerful rundowns.", score_breakdown, score
    elif score >= 50:
        return 3, "Strong - A solid, profitable hand with good suited and/or connected components. Playable in most positions.", score_breakdown, score
    elif score >= 30:
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
