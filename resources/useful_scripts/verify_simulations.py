import os
import json
import random
import sys

# Add project root to path to allow importing the simulation function
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

try:
    from monte_carlo_plo_hand_eval import simulate_hand_equity, ITERATIONS_PER_HAND
except ImportError as e:
    print(f"Error: Could not import the simulation function. Make sure this script is in the project root.")
    print(f"Details: {e}")
    sys.exit(1)

from treys import Card

STATS_DIR = os.path.join(project_root, 'plo_hand_stats')
TOLERANCE = 1.0  # Allowable margin of error in percent

def get_random_hand_record():
    """Finds data files, and picks a random one and a random hand from it."""
    if not os.path.isdir(STATS_DIR):
        print(f"Error: Statistics directory not found: {STATS_DIR}")
        return None

    json_files = [f for f in os.listdir(STATS_DIR) if f.startswith('hands_') and f.endswith('.json')]
    if not json_files:
        print("Error: No hand data files found in the stats directory.")
        return None

    random_file = random.choice(json_files)
    file_path = os.path.join(STATS_DIR, random_file)
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        return random.choice(data)
    except (IOError, json.JSONDecodeError, IndexError) as e:
        print(f"Error reading or parsing {random_file}: {e}")
        return None

def run_verification():
    """
    Selects one random hand, re-runs the simulation, and verifies the results.
    Returns True on success, False on failure.
    """
    stored_record = get_random_hand_record()
    if not stored_record:
        return False # Stop if we couldn't get a record

    hand_str = stored_record['hand']
    stored_win_pct = stored_record['win_pct']
    stored_split_pct = stored_record['split_pct']

    print(f"--- Verifying Hand: {hand_str} ---")
    print(f"Stored Win %: {stored_win_pct:.2f}, Stored Split %: {stored_split_pct:.2f}")
    print(f"Running new simulation with {ITERATIONS_PER_HAND:,} iterations...")

    hero_hand_tuple = tuple(sorted([hand_str[i:i+2] for i in range(0, len(hand_str), 2)], key=Card.new))

    new_results = simulate_hand_equity(hero_hand_tuple)
    new_win_pct = new_results['win_pct']
    new_split_pct = new_results['split_pct']

    print(f"New Win %: {new_win_pct:.2f}, New Split %: {new_split_pct:.2f}")

    win_diff = abs(new_win_pct - stored_win_pct)
    split_diff = abs(new_split_pct - stored_split_pct)

    if win_diff <= TOLERANCE and split_diff <= TOLERANCE:
        print(f"\n✅ PASSED: Results are within the {TOLERANCE}% tolerance.\n")
        return True
    else:
        print(f"\n❌ FAILED: Deviation is too high.")
        if win_diff > TOLERANCE:
            print(f"   - Win % deviation: {win_diff:.2f}%")
        if split_diff > TOLERANCE:
            print(f"   - Split % deviation: {split_diff:.2f}%")
        print("")
        return False

def main():
    """Main function to prompt the user and run the verifications."""
    while True:
        try:
            num_str = input(f"How many random hands would you like to test? [Default: 1]: ")
            if not num_str:
                num_to_run = 1
                break
            num_to_run = int(num_str)
            if num_to_run > 0:
                break
            else:
                print("Please enter a positive number.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    print(f"\nStarting verification for {num_to_run} random hand(s)...\n")
    success_count = 0
    for i in range(num_to_run):
        print(f"--- Test Run {i + 1} of {num_to_run} ---")
        if run_verification():
            success_count += 1

    print(f"--- Summary ---")
    print(f"Completed {num_to_run} tests. Passed: {success_count}, Failed: {num_to_run - success_count}.")

if __name__ == "__main__":
    main()
