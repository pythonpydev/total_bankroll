import itertools
import json
import random
from multiprocessing import Pool, cpu_count
from treys import Card, Deck, Evaluator
from tqdm import tqdm
import os

ITERATIONS_PER_HAND = 100000  # Number of simulations for each hand. Higher is more accurate but slower.

evaluator = Evaluator()

def get_best_plo_rank(hole_cards, board_cards):
    """
    Finds the best 5-card hand rank from a 4-card PLO hand and 5-card board.
    Uses the treys library evaluator.
    Args:
        hole_cards (list): A list of 4 treys Card objects.
        board_cards (list): A list of 5 treys Card objects.
    Returns:
        int: The rank of the best 5-card hand (lower is better).
    """
    best_rank = 7463  # A rank worse than any possible hand

    # Iterate through all combinations of 2 cards from the hand and 3 from the board
    for hole_combo in itertools.combinations(hole_cards, 2):
        for board_combo in itertools.combinations(board_cards, 3):
            rank = evaluator.evaluate(list(hole_combo), list(board_combo))
            if rank < best_rank:
                best_rank = rank
    return best_rank

def simulate_hand_equity(hero_hand_tuple):
    """
    Runs a Monte Carlo simulation for a single PLO hand against a random opponent hand.
    Designed to be used with multiprocessing.Pool.
    Args:
        hero_hand_tuple (tuple): A tuple of 4 card strings (e.g., ('As', 'Ks', 'Qs', 'Js')).
    Returns:
        dict: A dictionary containing the hand, win %, split %, and loss %.
    """
    wins = 0
    ties = 0
    losses = 0

    hero_hand_treys = [Card.new(c) for c in hero_hand_tuple]

    # --- Optimization: Create the remaining deck once outside the loop ---
    remaining_cards = list(Deck.GetFullDeck())
    for card in hero_hand_treys:
        remaining_cards.remove(card)

    for _ in range(ITERATIONS_PER_HAND):
        # --- Optimization: Use random.sample for much faster card selection ---
        # This is significantly faster than shuffling the whole deck each time.
        random_cards = random.sample(remaining_cards, 9)
        opponent_hand_treys = random_cards[:4]
        board_treys = random_cards[4:]

        # Evaluate hands
        hero_rank = get_best_plo_rank(hero_hand_treys, board_treys)
        opponent_rank = get_best_plo_rank(opponent_hand_treys, board_treys)

        # Tally results
        if hero_rank < opponent_rank:
            wins += 1
        elif hero_rank == opponent_rank:
            ties += 1
        else:
            losses += 1

    return {
        "hand": "".join(hero_hand_tuple),
        "win_pct": (wins / ITERATIONS_PER_HAND) * 100,
        "split_pct": (ties / ITERATIONS_PER_HAND) * 100,
        "loss_pct": (losses / ITERATIONS_PER_HAND) * 100,
    }

def main():
    """
    Main function to generate all PLO hands, run simulations in parallel,
    and save the results to a JSON file, with efficient, index-based progress
    saving and resuming.
    """
    # --- Constants and Configuration ---
    CHUNK_SIZE = 100  # How many hands to process before saving a file
    STATS_DIR = 'plo_hand_stats'
    RESUME_FILE = os.path.join(STATS_DIR, 'resume_info.json')
    FINAL_OUTPUT_DIR = os.path.join('src', 'total_bankroll', 'data')
    FINAL_OUTPUT_FILE = os.path.join(FINAL_OUTPUT_DIR, 'plo_hand_equity.json')

    # --- Setup Directories ---
    os.makedirs(STATS_DIR, exist_ok=True)
    os.makedirs(FINAL_OUTPUT_DIR, exist_ok=True)

    # --- Generate All Hands (in a deterministic, sequential order) ---
    print("Generating all unique PLO starting hands...")
    deck = Deck()
    all_card_strs = [Card.int_to_str(c) for c in deck.cards]
    all_plo_hands = list(itertools.combinations(all_card_strs, 4))
    total_hands_count = len(all_plo_hands)
    print(f"Generated {total_hands_count:,} unique hands.")

    # --- Efficient Resume Logic ---
    start_index = 0
    if os.path.exists(RESUME_FILE):
        try:
            with open(RESUME_FILE, 'r') as f:
                resume_data = json.load(f)
                # Get the index of the last successfully processed hand
                start_index = resume_data.get('last_processed_index', -1) + 1
        except (json.JSONDecodeError, FileNotFoundError):
            print("Warning: resume_info.json is corrupted or unreadable. Starting from scratch.")
            start_index = 0

    if start_index > 0:
        print(f"Resuming simulation from hand index {start_index:,}.")

    # Slice the list to get only the hands that need to be simulated
    hands_to_simulate = all_plo_hands[start_index:]
    num_to_simulate = len(hands_to_simulate)

    if num_to_simulate == 0:
        print("All hands have already been simulated.")
    else:
        print(f"Starting simulation for {num_to_simulate:,} remaining hands.")
        num_cores = cpu_count()
        print(f"Using {num_cores} cores, simulating {ITERATIONS_PER_HAND:,} iterations per hand.")

        results_chunk = []
        
        # Use Pool to parallelize the simulations
        # Using imap (instead of imap_unordered) to get results in the same order as input
        with Pool(processes=num_cores) as pool:
            with tqdm(total=num_to_simulate, desc="Simulating Hand Equities") as pbar:
                # The 'chunksize' argument can improve performance for large iterables
                for i, result in enumerate(pool.imap(simulate_hand_equity, hands_to_simulate, chunksize=10)):
                    results_chunk.append(result)
                    pbar.update()

                    # When the chunk is full, save it and update the resume file
                    if len(results_chunk) >= CHUNK_SIZE:
                        current_absolute_index = start_index + i
                        chunk_start_index = current_absolute_index - CHUNK_SIZE + 1
                        
                        # Save the chunk of results
                        chunk_file_name = f"hands_{chunk_start_index:06d}_to_{current_absolute_index:06d}.json"
                        with open(os.path.join(STATS_DIR, chunk_file_name), 'w') as f:
                            json.dump(results_chunk, f)
                        
                        # Update the resume file with the last processed index
                        with open(RESUME_FILE, 'w') as f:
                            json.dump({'last_processed_index': current_absolute_index}, f)
                        
                        results_chunk = [] # Reset for the next chunk

                # Save any remaining results in the last partial chunk
                if results_chunk:
                    last_absolute_index = start_index + num_to_simulate - 1
                    chunk_start_index = last_absolute_index - len(results_chunk) + 1
                    
                    chunk_file_name = f"hands_{chunk_start_index:06d}_to_{last_absolute_index:06d}.json"
                    with open(os.path.join(STATS_DIR, chunk_file_name), 'w') as f:
                        json.dump(results_chunk, f)
                    
                    with open(RESUME_FILE, 'w') as f:
                        json.dump({'last_processed_index': last_absolute_index}, f)

    # --- Combine all results into a single file ---
    print("\nCombining all saved statistics...")
    all_results = []
    # Sort filenames to ensure they are read in order
    for filename in sorted(os.listdir(STATS_DIR)):
        if filename.endswith('.json') and filename.startswith('hands_'):
            filepath = os.path.join(STATS_DIR, filename)
            with open(filepath, 'r') as f:
                try:
                    all_results.extend(json.load(f))
                except json.JSONDecodeError:
                    print(f"Warning: Could not parse {filename}. It might be corrupted.")

    if not all_results:
        print("No results found to combine.")
        return

    print(f"Loaded {len(all_results):,} total hand equities.")
    
    # Sort final results by win_pct for easier analysis
    all_results.sort(key=lambda x: x['win_pct'], reverse=True)

    # Save the final combined and sorted file
    with open(FINAL_OUTPUT_FILE, 'w') as f:
        json.dump(all_results, f, indent=2)

    print(f"Successfully saved combined equities to {FINAL_OUTPUT_FILE}")
    print("\n--- Top 5 Hands ---")
    for i in range(min(5, len(all_results))):
        hand_data = all_results[i]
        print(f"{i+1}. {hand_data['hand']}: Win {hand_data['win_pct']:.2f}%, Split {hand_data['split_pct']:.2f}%")

if __name__ == "__main__":
    main()
