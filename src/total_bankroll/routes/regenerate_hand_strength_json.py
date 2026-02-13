import os
import sys
import json
from itertools import combinations

# Add the project's src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from total_bankroll.routes.hand_eval import evaluate_hand_strength

def generate_all_plo_hands():
    """Generates all 270,725 unique PLO starting hands."""
    ranks = "23456789TJQKA"
    suits = "shdc"
    deck = [r + s for r in ranks for s in suits]
    
    # Using combinations to get all unique 4-card hands
    for hand_tuple in combinations(deck, 4):
        yield "".join(hand_tuple)

def regenerate_hand_strength_file():
    """
    Generates all PLO hands, evaluates their strength using the corrected
    `evaluate_hand_strength` function, and saves the results to a JSON file.
    """
    print("Starting regeneration of hand strength data...")
    
    all_hands_data = []
    hand_generator = generate_all_plo_hands()
    
    for i, hand_string in enumerate(hand_generator):
        tier, _, _, _ = evaluate_hand_strength(hand_string)
        all_hands_data.append({
            "hand": hand_string,
            "tier": tier
        })
        if (i + 1) % 10000 == 0:
            print(f"Processed {i + 1} hands...")

    # Path to the data file within the application structure
    output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'total_bankroll', 'data', 'hand_strength_all.json'))
    
    print(f"\nProcessed a total of {len(all_hands_data)} hands.")
    print(f"Saving updated data to {output_path}...")

    with open(output_path, 'w') as f:
        json.dump(all_hands_data, f, indent=2)
        
    print("Regeneration complete. The hand_strength_all.json file has been updated with accurate ratings.")

if __name__ == "__main__":
    regenerate_hand_strength_file()