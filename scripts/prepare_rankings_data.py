import os
import pandas as pd
import sys

# Add the 'src' directory to the Python path to allow importing 'total_bankroll'
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

def prepare_plo_rankings_data():
    """
    Reads the raw evaluated CSV, cleans and transforms the data,
    and saves it to an efficient Feather file format for fast loading in the app.
    """
    print("Starting data preparation...")

    data_dir = os.path.join(src_path, 'total_bankroll', 'data')
    input_csv_path = os.path.join(data_dir, 'plo_hands_evaluated.csv')
    output_feather_path = os.path.join(data_dir, 'plo_hands_rankings.feather')

    if not os.path.exists(input_csv_path):
        print(f"Error: Input file not found at {input_csv_path}")
        return

    try:
        print(f"Reading raw data from {input_csv_path}...")
        df = pd.read_csv(input_csv_path, low_memory=False)
        print(f"Loaded {len(df)} rows.")

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

        # --- 6. Drop Invalid Rows ---
        df = df.dropna(subset=['Hand', 'Tier', 'Rating Score'])
        
        # --- 7. Optimize Data Types for Memory ---
        df['Tier'] = df['Tier'].astype('int8')
        df['Rating Score'] = df['Rating Score'].astype('float32')
        df['Rating Reason'] = df['Rating Reason'].astype('category')
        df['RanksOnly'] = df['RanksOnly'].astype('category')
        
        # Set 'Hand' as the index for faster lookups
        df = df.set_index('Hand')

        print("Data transformation complete. Final columns:", list(df.columns))
        print("\nDataFrame Info:")
        df.info(memory_usage='deep')

        # --- 8. Save to Feather File ---
        df.reset_index().to_feather(output_feather_path)
        print(f"\nSuccessfully saved optimized data to {output_feather_path}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Before running, ensure you have pyarrow installed:
    # pip install pyarrow
    prepare_plo_rankings_data()