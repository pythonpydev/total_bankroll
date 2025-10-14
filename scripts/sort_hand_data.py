import pandas as pd
import os


def sort_hand_string(hand_str):
    """
    Sorts a 4-card hand string (e.g., '4sAcKd5d') by rank in descending order.

    Args:
        hand_str (str): The hand string to sort.

    Returns:
        str: The sorted hand string (e.g., 'AcKd5d4s').
    """
    # Define the order of ranks from highest to lowest for sorting
    rank_order = "AKQJT98765432"
    suit_order = "shdc"

    # Clean the hand string by removing commas and spaces
    if isinstance(hand_str, str):
        hand_str = hand_str.replace(',', '').replace(' ', '')

    # Handle cases where the hand string might be invalid or not a string
    if not isinstance(hand_str, str) or len(hand_str) != 8:
        return hand_str  # Return the original value if it's not a standard 8-char hand

    # Split the hand string into a list of 2-character cards
    cards = [hand_str[i:i+2] for i in range(0, len(hand_str), 2)]

    # Sort the list of cards. The key for sorting is a tuple:
    # 1. The position of the card's rank in 'rank_order' (primary sort key).
    # 2. The position of the card's suit in 'suit_order' (secondary sort key).
    try:
        sorted_cards = sorted(cards, key=lambda card: (rank_order.index(card[0].upper()), suit_order.index(card[1].lower())))
    except ValueError as e:
        print(f"Warning: Could not sort hand '{hand_str}'. Invalid character found. Error: {e}")
        return hand_str

    # Join the sorted cards back into a single string
    return "".join(sorted_cards)


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