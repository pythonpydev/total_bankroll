import os
import sys
import pandas as pd

# Add the 'src' directory to the Python path to allow importing 'total_bankroll'
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, src_path)
from total_bankroll.data_utils import sort_hand_string

def main():
    """
    Main function to read, process, and save the hand data.
    """
    # Define file paths relative to the project root
    input_csv_path = os.path.join('src', 'total_bankroll', 'data', 'plo_hands_evaluated.csv')
    output_csv_path = os.path.join('src', 'total_bankroll', 'data', 'plo_hands_evaluated_sorted.csv')

    print(f"Reading hand data from: {input_csv_path}")
    df = pd.read_csv(input_csv_path)

    # Assuming the column with hands is named 'cards'
    print("Sorting hands in the 'cards' column...")
    df['cards'] = df['cards'].apply(sort_hand_string)

    print(f"Saving sorted data to: {output_csv_path}")
    df.to_csv(output_csv_path, index=False)

    print("\nProcessing complete. First 5 rows of the new file:")
    print(df.head())

if __name__ == "__main__":
    main()