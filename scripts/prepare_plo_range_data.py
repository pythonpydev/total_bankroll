import os
import sys
import pandas as pd

# Add the 'src' directory to the Python path to allow importing 'total_bankroll'
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, src_path)

def main():
    """
    Reads the evaluated PLO hands, calculates percentile ranks,
    and saves the data in an optimized Feather format for the PLO Range Tool.
    """
    # Define file paths relative to the project root
    data_dir = os.path.join(project_root, 'src', 'total_bankroll', 'data')
    input_csv_path = os.path.join(data_dir, 'plo_hands_evaluated.csv')
    output_feather_path = os.path.join(data_dir, 'plo_range_data.feather')

    print(f"Reading hand data from: {input_csv_path}")
    try:
        df = pd.read_csv(input_csv_path)
    except FileNotFoundError:
        print(f"Error: Input file not found at {input_csv_path}")
        return

    print("Processing data...")

    # Rename columns to the final format expected by the frontend API
    # The source CSV has 'cards', 'strength', 'rating'
    df_renamed = df.rename(columns={
        'cards': 'hand',
        'strength': 'strength',
        'rating': 'type'
    })

    # Ensure 'strength' is numeric before sorting
    df_renamed['strength'] = pd.to_numeric(df_renamed['strength'], errors='coerce')
    df_renamed.dropna(subset=['strength'], inplace=True)

    # Sort by 'strength' in descending order to rank hands from best to worst
    df_sorted = df_renamed.sort_values(by='strength', ascending=False).reset_index(drop=True)

    # Calculate percentile rank
    df_sorted['percentile'] = (df_sorted.index / (len(df_sorted) - 1)) * 100 if len(df_sorted) > 1 else 0

    # Select only the columns needed for the API to keep the file small
    final_df = df_sorted[['hand', 'type', 'strength', 'percentile']]

    print(f"Saving optimized data to: {output_feather_path}")
    final_df.to_feather(output_feather_path)

    print("\nProcessing complete. First 5 rows of the new data:")
    print(final_df.head())

if __name__ == "__main__":
    main()