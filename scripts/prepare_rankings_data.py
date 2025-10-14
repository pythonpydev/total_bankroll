import os
import sys
import logging

# Add the 'src' directory to the Python path to allow importing 'total_bankroll'
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from total_bankroll.data_utils import prepare_plo_rankings_data

def main():
    """
    Reads the raw evaluated CSV, cleans and transforms the data,
    and saves it to an efficient Feather file format for fast loading in the app.
    """
    print("Starting data preparation...")

    data_dir = os.path.join(src_path, 'total_bankroll', 'data')
    input_csv_path = os.path.join(data_dir, 'plo_hands_evaluated.csv')
    output_feather_path = os.path.join(data_dir, 'plo_hands_rankings.feather')

    try:
        prepare_plo_rankings_data(input_csv_path, output_feather_path)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Configure basic logging for the script
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

    # Before running, ensure you have pyarrow installed:
    # pip install pyarrow
    main()