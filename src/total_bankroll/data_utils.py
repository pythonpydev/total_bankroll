"""Utilities for preparing and loading data for the application."""

import os
import pandas as pd
import logging

log = logging.getLogger(__name__)

def prepare_plo_rankings_data(input_csv_path, output_feather_path):
    """
    Reads the raw evaluated CSV, cleans and transforms the data,
    and saves it to an efficient Feather file format for fast loading in the app.

    Args:
        input_csv_path (str): The full path to the source CSV file.
        output_feather_path (str): The full path where the output Feather file will be saved.
    """
    log.info("Starting data preparation...")

    if not os.path.exists(input_csv_path):
        log.error(f"Error: Input file not found at {input_csv_path}")
        raise FileNotFoundError(f"Input file not found at {input_csv_path}")

    try:
        log.info(f"Reading raw data from {input_csv_path}...")
        df = pd.read_csv(input_csv_path, low_memory=False)
        log.info(f"Loaded {len(df)} rows.")

        # --- 1. Column Renaming ---
        column_mapping = {}
        for col in df.columns:
            col_lower = col.lower().strip()
            if col_lower in ['cards', 'hand']:
                column_mapping[col] = 'Hand'
            elif col_lower in ['rating', 'tier']:
                column_mapping[col] = 'Tier'
            elif col_lower in ['score', 'rating score', 'rating_score', 'strength']:
                column_mapping[col] = 'Rating Score'
        df = df.rename(columns=column_mapping)

        # --- 2. Type Conversion and Cleaning ---
        df['Rating Score'] = pd.to_numeric(df['Rating Score'], errors='coerce')
        df['Hand'] = df['Hand'].str.replace(',', '').str.strip()

        # --- 3. Tier Calculation ---
        def score_to_tier(score):
            if pd.isna(score): return 5
            if score >= 80: return 1
            if score >= 65: return 2
            if score >= 45: return 3
            if score >= 25: return 4
            return 5

        df['Tier'] = df['Rating Score'].apply(score_to_tier).astype('int8')

        # --- 4. Add Rating Reason ---
        tier_reasons = {
            1: "Elite - A top-tier hand with immense nut potential",
            2: "Premium - A very strong hand with excellent coordination",
            3: "Strong - A solid, profitable hand",
            4: "Playable - A speculative hand best played with position",
            5: "Trash/Marginal - A weak hand with poor coordination"
        }
        df['Rating Reason'] = df['Tier'].map(tier_reasons).fillna("Unrated hand")

        # --- 5. Create RanksOnly Column for Searching ---
        rank_order = "AKQJT98765432"
        df['RanksOnly'] = df['Hand'].apply(
            lambda h: "".join(sorted([c for i, c in enumerate(h) if i % 2 == 0], key=lambda r: rank_order.index(r.upper())))
        )

        # --- 6. Finalize and Optimize ---
        df = df.dropna(subset=['Hand', 'Tier', 'Rating Score'])
        df['Tier'] = df['Tier'].astype('int8')
        df['Rating Score'] = df['Rating Score'].astype('float32')
        df['Rating Reason'] = df['Rating Reason'].astype('category')
        df['RanksOnly'] = df['RanksOnly'].astype('category')

        # --- 7. Save to Feather File ---
        df.to_feather(output_feather_path)
        log.info(f"\nSuccessfully saved optimized data to {output_feather_path}")

    except Exception as e:
        log.error(f"An error occurred during data preparation: {e}")
        raise

def sort_hand_string(hand_str: str) -> str:
    """
    Sorts a card hand string (e.g., '4sAcKd5d') by rank in descending order, then by suit.

    Args:
        hand_str: The hand string to sort.

    Returns:
        The sorted hand string (e.g., 'AsKsAc4s').
    """
    rank_order = "AKQJT98765432"
    suit_order = "shdc"  # Spades > Hearts > Diamonds > Clubs

    if not isinstance(hand_str, str):
        return hand_str  # Return as is if not a string

    # Clean the hand string by removing commas and spaces
    cleaned_hand_str = hand_str.replace(',', '').replace(' ', '')

    # Validate length after cleaning; odd length means it's a partial/invalid hand
    if len(cleaned_hand_str) % 2 != 0:
        log.debug(f"Partial hand string '{cleaned_hand_str}' has odd length, not sorting.")
        return hand_str

    cards = [cleaned_hand_str[i:i+2] for i in range(0, len(cleaned_hand_str), 2)]

    try:
        sorted_cards = sorted(cards, key=lambda card: (rank_order.index(card[0].upper()), suit_order.index(card[1].lower())))
    except (ValueError, IndexError) as e:
        log.warning(f"Could not sort hand '{hand_str}'. Invalid character found. Error: {e}")
        return hand_str

    return "".join(sorted_cards)