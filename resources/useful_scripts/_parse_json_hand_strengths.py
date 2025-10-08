import json
from collections import Counter

rank_map = {
    'A': 14, 'K': 13, 'Q': 12, 'J': 11, 'T': 10,
    '9': 9, '8': 8, '7': 7, '6': 6, '5': 5, '4': 4, '3': 3, '2': 2
}

def parse_hand(hand_str):
    ranks = []
    suits = []
    for i in range(0, len(hand_str), 2):
        r = hand_str[i]
        s = hand_str[i + 1]
        ranks.append(rank_map[r])
        suits.append(s)
    return sorted(ranks, reverse=True), suits, hand_str

def get_suited_type(suits):
    count = Counter(suits)
    values = sorted(count.values())
    if values == [2, 2]:
        return 'ds'
    elif values in [[1, 1, 2], [1, 3], [4]]:
        return 'ss'
    else:
        return 'rainbow'

def get_pairs(ranks):
    count = Counter(ranks)
    pairs = [r for r, c in count.items() if c == 2]
    trips = [r for r, c in count.items() if c >= 3]
    return pairs, trips

def is_ace_suited(hand_str, suits, ranks, suited_type):
    if suited_type != 'ss' or 14 not in ranks:
        return False
    count = Counter(suits)
    max_suit = max(count, key=count.get)
    if count[max_suit] < 2:
        return False
    ace_suits = []
    for i in range(0, len(hand_str), 2):
        if hand_str[i] == 'A':
            ace_suits.append(hand_str[i + 1])
    return max_suit in ace_suits

def classify_hand(hand_str):
    ranks, suits, hand_str = parse_hand(hand_str)
    suited_type = get_suited_type(suits)
    pairs, trips = get_pairs(ranks)
    has_aa = 14 in pairs
    gaps_list = [ranks[i] - ranks[i+1] - 1 for i in range(3)]
    total_gaps = sum(gaps_list)
    is_top_gapped = any(g > 0 for g in gaps_list[:-1])

    # Category 1: PREMIUM (MAGNUM) - AA ds with high connectors or second big pair
    if has_aa and suited_type == 'ds':
        remaining_pairs = [p for p in pairs if p != 14]
        if remaining_pairs:
            second_pair = remaining_pairs[0]
            if second_pair >= 10:
                return "1. PREMIUM (MAGNUM)"
        else:
            other_ranks = [r for r in set(ranks) if r != 14]
            if len(other_ranks) == 2 and all(r >= 10 for r in other_ranks):
                other_sorted = sorted(other_ranks, reverse=True)
                if other_sorted[0] - other_sorted[1] <= 3:
                    return "1. PREMIUM (MAGNUM)"

    # Category 2: PREMIUM (Top Rundowns/Pairs)
    if suited_type in ['ds', 'ss']:
        if len(pairs) == 2:
            p1, p2 = sorted(pairs, reverse=True)
            if p1 >= 10 and p2 >= 10:
                return "2. PREMIUM (Top Rundowns/Pairs)"
        elif len(pairs) == 0:
            if total_gaps == 0 and ranks[3] >= 8:
                return "2. PREMIUM (Top Rundowns/Pairs)"

    # Category 3: SPECULATIVE
    if suited_type in ['ds', 'ss']:
        if is_ace_suited(hand_str, suits, ranks, suited_type):
            return "3. SPECULATIVE"
        if total_gaps <= 2 and not is_top_gapped:
            return "3. SPECULATIVE"
        if 14 in ranks and total_gaps <= 3 and not is_top_gapped:
            return "3. SPECULATIVE"

    # Category 4: MARGINAL
    if suited_type in ['ds', 'ss']:
        high_count = sum(1 for r in ranks if r >= 10)
        if high_count == 3:
            return "4. MARGINAL"
        if total_gaps == 1 and is_top_gapped:
            return "4. MARGINAL"

    # Category 5: TRASH / AVOID
    return "5. TRASH / AVOID"

# Load the JSON file
with open('hand_strength_all.json', 'r') as f:
    data = json.load(f)

# Process each hand and correct the tier
for item in data:
    hand = item['hand']
    corrected_tier = classify_hand(hand)
    item['tier'] = corrected_tier

# Save the corrected JSON
with open('corrected_hand_strength_all.json', 'w') as f:
    json.dump(data, f, indent=4)

print("JSON file processed and corrections saved to 'corrected_hand_strength_all.json'.")