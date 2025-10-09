import os
import json
import random
import pytest
from treys import Card

# To test the simulation function, we need to import it from the script.
# This requires adding the project root to the Python path so the import works.
import sys

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Now we can import the function to be tested
from monte_carlo_plo_hand_eval import simulate_hand_equity, ITERATIONS_PER_HAND

STATS_DIR = os.path.join(project_root, 'plo_hand_stats')
TOLERANCE = 1.0  # Allowable margin of error in percent (e.g., 1.0 for +/- 1%)


@pytest.fixture
def random_hand_data_from_files():
    """Pytest fixture to find data files, and pick a random one and a random hand from it."""
    # Ensure the stats directory exists
    if not os.path.isdir(STATS_DIR):
        pytest.skip(f"Statistics directory not found: {STATS_DIR}")

    # Find all valid hand data files
    json_files = [f for f in os.listdir(STATS_DIR) if f.startswith('hands_') and f.endswith('.json')]
    if not json_files:
        pytest.skip("No hand data files found in the stats directory.")

    # Pick a random file and load its content
    random_file = random.choice(json_files)
    file_path = os.path.join(STATS_DIR, random_file)
    with open(file_path, 'r') as f:
        data = json.load(f)

    # Pick a random hand record from the file
    random_record = random.choice(data)
    return random_record


def test_simulation_verification(random_hand_data_from_files, iteration):
    """
    Tests that re-running a simulation for a specific hand produces results
    that are statistically close to the pre-calculated results.
    This test is parametrized by the --num-tests command line option.
    """
    print(f"\n--- Verification Run: {iteration + 1} ---")
    stored_record = random_hand_data_from_files

    # Extract the hand and its stored results
    hand_str = stored_record['hand']
    stored_win_pct = stored_record['win_pct']
    stored_split_pct = stored_record['split_pct']

    print(f"Verifying hand: {hand_str}")
    print(f"Stored Win %: {stored_win_pct:.2f}")
    print(f"Running new simulation with {ITERATIONS_PER_HAND} iterations...")

    # Re-create the hand tuple from the string, ensuring canonical order
    hero_hand_tuple = tuple(sorted([hand_str[i:i+2] for i in range(0, len(hand_str), 2)], key=Card.new))

    # Re-run the simulation for this hand to get fresh results
    new_results = simulate_hand_equity(hero_hand_tuple)
    new_win_pct = new_results['win_pct']
    new_split_pct = new_results['split_pct']

    print(f"New Win %: {new_win_pct:.2f}")

    # Assert that the new results are within the tolerance margin of the stored results
    # We use pytest.approx to handle floating point comparisons and statistical variance.
    assert new_win_pct == pytest.approx(stored_win_pct, abs=TOLERANCE), \
        f"Win % deviation is too high. Stored: {stored_win_pct:.2f}, New: {new_win_pct:.2f}"

    assert new_split_pct == pytest.approx(stored_split_pct, abs=TOLERANCE), \
        f"Split % deviation is too high. Stored: {stored_split_pct:.2f}, New: {new_split_pct:.2f}"

    # The loss is just the remainder, so checking win/split is sufficient
    # loss_pct = 100 - win_pct - split_pct

