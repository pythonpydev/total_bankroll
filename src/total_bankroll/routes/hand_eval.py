"""PLO hand evaluation and spr quiz."""

import re
from typing import TypedDict, Counter as CounterType, Dict, List
import csv
from collections import Counter
import logging
import json
import os
import random
import markdown
from flask import Blueprint, render_template, request, session, redirect, url_for, flash, current_app, jsonify
from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, SubmitField, SelectField, RadioField
from wtforms.validators import DataRequired, Optional, ValidationError
from operator import itemgetter
from . import algo
import pandas as pd  # Added for optimization

hand_eval_bp = Blueprint('hand_eval', __name__)

class ButtonPositionForm(FlaskForm):
    button_position = IntegerField('Button Position')
    submit = SubmitField('Submit')

POSITIONS = [('UTG', 'UTG'), ('HJ', 'HJ'), ('CO', 'CO'), ('BTN', 'BTN'), ('SB', 'SB'), ('BB', 'BB')]

class HandForm(FlaskForm):
    small_blind = IntegerField('Small Blind', validators=[DataRequired()])
    big_blind = IntegerField('Big Blind', validators=[DataRequired()])
    hero_stack = IntegerField("Hero's Chip Stack", validators=[DataRequired()])
    hero_position = SelectField("Hero's Position", choices=POSITIONS, validators=[DataRequired()])
    hero_hand = StringField("Hero's Hand", validators=[DataRequired()])
    board = StringField('Board Cards', validators=[DataRequired()]) # Keep DataRequired for presence
    opponent_stack = IntegerField("Opponent's Chip Stack", validators=[DataRequired()])
    opponent_position = SelectField("Opponent's Position", choices=POSITIONS, validators=[DataRequired()])
    opponent_hand = StringField("Opponent's Hand", validators=[DataRequired()])
    pot_size = IntegerField('Pot Size', validators=[DataRequired()])
    bet_size = IntegerField('Bet Size', validators=[Optional()])
    submit = SubmitField('Submit')

    def validate_board(self, field):
        # Board can be 3, 4, or 5 cards long (6, 8, or 10 characters)
        if len(field.data) not in [6, 8, 10]:
            raise ValidationError("Board must contain 3, 4, or 5 cards.")

    def validate_opponent_position(self, field):
        if field.data and self.hero_position.data and field.data == self.hero_position.data:
            raise ValidationError("Hero and Opponent cannot be in the same position.")

    def validate_bet_size(self, field):
        if field.data is not None and self.pot_size.data is not None:
            if field.data > self.pot_size.data:
                raise ValidationError("Bet size cannot be greater than the pot size.")

    def validate(self, **kwargs):
        # Run parent validation first
        if not super().validate(**kwargs):
            return False
        # Custom validation for unique cards across all fields
        all_cards_str = self.hero_hand.data + self.opponent_hand.data + self.board.data
        card_list = [all_cards_str[i:i+2] for i in range(0, len(all_cards_str), 2)]
        if len(card_list) != len(set(card_list)):
            raise ValidationError("Duplicate cards found between Hero's Hand, Opponent's Hand, and the Board.")
        return True

class HandStrengthForm(FlaskForm):
    """Form for submitting a hand for strength evaluation."""
    hand = StringField("Enter PLO Hand (e.g., AsKsQhJh)", validators=[DataRequired()], render_kw={"placeholder": "e.g., AsKsQhJh or AA44ds"})
    position = SelectField("Your Position", choices=POSITIONS, validators=[DataRequired()])
    submit = SubmitField('Evaluate Hand')

    def validate_hand(self, field):
        hand_str = field.data.replace(" ", "")
        if len(hand_str) != 8:
            raise ValidationError("Hand must contain exactly 4 cards (8 characters).")
        
        ranks = "23456789TJQKA"
        suits = "shdc"
        cards = [hand_str[i:i+2].upper() for i in range(0, len(hand_str), 2)]

        if len(cards) != 4:
            raise ValidationError("Invalid hand format. Use format like 'AsKsQhJh'.")

        seen_cards = set()
        for card in cards:
            rank = card[0]
            suit = card[1].lower()
            if rank not in ranks or suit not in suits:
                raise ValidationError(f"Invalid card '{card}'. Use ranks 2-9, T, J, Q, K, A and suits s, h, d, c.")
            if card in seen_cards:
                raise ValidationError(f"Duplicate card '{card}' found in hand.")
            seen_cards.add(card)

class HandProperties(TypedDict):
    """A dictionary holding the calculated properties of a PLO hand."""
    rank_counts: CounterType[int]
    suit_counts: CounterType[str]
    pairs: Dict[int, int]
    trips: Dict[int, int]
    quads: Dict[int, int]
    is_double_suited: bool
    is_single_suited: bool
    suited_ranks: Dict[str, List[int]]
    max_streak: int
    is_broadway_streak: bool
    broadway_cards: List[int]
    danglers: int

def _get_hand_properties(ranks: List[int], suits: List[str]) -> HandProperties:
    """
    Analyzes a PLO hand's ranks and suits to determine its key properties.

    Args:
        ranks: A sorted list of 4 integer card ranks (e.g., [12, 12, 11, 10] for AAKQ).
        suits: A list of 4 string card suits (e.g., ['s', 'h', 'd', 'c']).

    Returns:
        A HandProperties dictionary containing the calculated properties of the hand.
    """
    ranks_str = "23456789TJQKA"
    properties: HandProperties = {}  # type: ignore

    properties['rank_counts'] = Counter(ranks)
    properties['suit_counts'] = Counter(suits)
    properties['pairs'] = {r: c for r, c in properties['rank_counts'].items() if c == 2}
    properties['trips'] = {r: c for r, c in properties['rank_counts'].items() if c == 3}
    properties['quads'] = {r: c for r, c in properties['rank_counts'].items() if c == 4}
    properties['is_double_suited'] = list(properties['suit_counts'].values()).count(2) == 2
    properties['is_single_suited'] = max(properties['suit_counts'].values()) >= 2

    suited_ranks = {}
    for i, suit in enumerate(suits):
        if suit not in suited_ranks: suited_ranks[suit] = []
        suited_ranks[suit].append(ranks[i])
    properties['suited_ranks'] = suited_ranks

    unique_ranks = sorted(list(set(ranks)), reverse=True)
    max_streak = 0
    if len(unique_ranks) > 1:
        current_streak = 1
        for i in range(1, len(unique_ranks)):
            if unique_ranks[i-1] - unique_ranks[i] == 1:
                current_streak += 1
            else:
                max_streak = max(max_streak, current_streak)
                current_streak = 1
        max_streak = max(max_streak, current_streak)
    properties['max_streak'] = max_streak
    return properties

def evaluate_hand_strength(hand_string: str) -> tuple[int, str, list, float]:
    """
    Evaluates a PLO hand string and assigns it to a tier based on heuristics
    point-based heuristic system. Returns tier, reason, score breakdown, and total score.
    """
    # 1. Parse hand into ranks and suits
    ranks_str = "23456789TJQKA"
    hand_string = hand_string.replace(" ", "").upper()
    cards = [hand_string[i:i+2] for i in range(0, 8, 2)]
    
    try:
        ranks_unsorted = [ranks_str.index(c[0]) for c in cards]
        ranks = sorted(ranks_unsorted, reverse=True)
        suits = [c[1].lower() for c in cards]
    except ValueError as e:
        raise ValueError(f"Invalid card rank found in hand '{hand_string}'. {e}")
    
    # 2. Get hand properties from helper function
    props = _get_hand_properties(ranks, suits)
    score = 0
    score_breakdown = []
    
    # --- 3. Score Calculation ---
    
    # a) Pair scoring (updated with tiered system)
    # Handle trips/quads first (new addition)
    if props['quads']:
        for rank in props['quads']:
            points = round((rank + 1) * 10, 1)
            score += points
            rank_name = ranks_str[rank]
            score_breakdown.append((f"Quads of {rank_name}s", f"+{points}"))
    elif props['trips']:
        for rank in props['trips']:
            points = round((rank + 1) * 4, 1)
            score += points
            rank_name = ranks_str[rank]
            score_breakdown.append((f"Trips of {rank_name}s", f"+{points}"))
    
    # Pairs with tiered scoring
    if props['pairs']:
        for rank in sorted(props['pairs'], reverse=True):
            pair_rank_name = ranks_str[rank]
            if rank >= ranks_str.index('Q'):  # Premium: Q=10, K=11, A=12
                points = round((rank + 1) * 3.5 + 10, 1)
                tier_name = "Premium"
            elif rank >= ranks_str.index('7'):  # Mid: 7=5 to J=9 (T=8, J=9)
                points = round((rank + 1) * 2.5 + 5, 1)
                tier_name = "Mid"
            else:  # Low: <7 (0-4)
                points = round((rank + 1) * 1.5, 1)
                tier_name = "Low"
            
            score += points
            score_breakdown.append((f"{tier_name} Pair of {pair_rank_name}s", f"+{points}"))
        
        # Two Pair Bonus
        if len(props['pairs']) == 2:
            bonus = 10
            pair_ranks = list(props['pairs'].keys())
            if all(r >= ranks_str.index('7') for r in pair_ranks):
                bonus += 5
                score_breakdown.append(("High/Mid Two Pair Bonus", f"+{bonus}"))
            else:
                score_breakdown.append(("Two Pair Bonus", f"+{bonus}"))
            score += bonus
    
    # b) Suitedness scoring
    if props['is_double_suited']:
        score += 25
        score_breakdown.append(("Double-Suited", "+25"))
        # Nut suit bonus
        for suit_ranks_list in props['suited_ranks'].values():
            if len(suit_ranks_list) >= 2 and ranks_str.index('A') in suit_ranks_list:
                score += 5
                score_breakdown.append(("Nut Suit Bonus", "+5"))
                break
    elif props['is_single_suited']:
        score += 10
        score_breakdown.append(("Single-Suited", "+10"))
        # Nut suit bonus
        ace_rank = ranks_str.index('A')
        if ace_rank in props['suited_ranks'].get(max(props['suit_counts'], key=props['suit_counts'].get), []):
            score += 5
            score_breakdown.append(("Nut Suit Bonus", "+5"))
    
    # Rainbow penalty (new)
    if max(props['suit_counts'].values()) == 1:
        score -= 10
        score_breakdown.append(("Rainbow Penalty", "-10"))
    
    # c) Connectivity scoring (updated to subset-aware)
    if props['max_streak'] >= 4:
        score += 25
        score_breakdown.append(("Full Rundown (4-card streak)", "+25"))
    elif props['max_streak'] == 3:
        score += 15
        score_breakdown.append(("Strong Partial Rundown (3-card streak)", "+15"))
    elif props['max_streak'] == 2:
        score += 5
        score_breakdown.append(("Basic Connectors (2-card streak)", "+5"))
    
    # Wheel bonus (new)
    ace_rank = ranks_str.index('A')
    low_ranks = [r for r in ranks_unsorted if r <= ranks_str.index('5')]
    if ace_rank in ranks_unsorted and len(low_ranks) >= 2:
        bonus = 5 * len(low_ranks)
        score += bonus
        score_breakdown.append((f"Wheel Potential ({len(low_ranks)+1} low cards w/ A)", f"+{bonus}"))
    
    # d) Suited connector bonuses (new)
    ace_rank = ranks_str.index('A')
    for suit, suit_ranks_list in props['suited_ranks'].items():
        if len(suit_ranks_list) >= 2:
            suit_ranks_sorted = sorted(suit_ranks_list, reverse=True)
            for j in range(1, len(suit_ranks_sorted)):
                diff = suit_ranks_sorted[j-1] - suit_ranks_sorted[j]
                if diff <= 2:
                    points = 5 if diff == 1 else 3
                    score += points
                    score_breakdown.append((f"Suited Connector/Gapper in {suit.upper()}", f"+{points}"))
                    if ace_rank in suit_ranks_sorted:
                        score += 3
                        score_breakdown.append(("Nut Suited Connector Bonus", "+3"))
                    break
    
    # e) High-card / Broadway scoring (adjusted)
    broadway_cards = [r for r in ranks_unsorted if r >= ranks_str.index('T')]
    if broadway_cards:
        points = len(broadway_cards) * 5
        score += points
        score_breakdown.append((f"{len(broadway_cards)} Broadway Card(s)", f"+{points}"))
        if len(broadway_cards) == 4:
            score += 15
            score_breakdown.append(("All Broadway Bonus", "+15"))
    
    # f) Refined dangler penalties (new)
    danglers = 0
    for i in range(len(ranks_unsorted)):
        neighbors = [abs(ranks_unsorted[i] - ranks_unsorted[j]) for j in range(len(ranks_unsorted)) if i != j]
        min_dist = min(neighbors) if neighbors else 99
        if min_dist > 3:
            danglers += 1
    if danglers > 0:
        penalty = danglers * 5
        if len(broadway_cards) >= 3 or props['is_double_suited']:
            penalty /= 2
        penalty = round(penalty, 1)
        score -= penalty
        score_breakdown.append((f"Dangler Penalty ({danglers} isolated cards)", f"-{penalty}"))
    
    # g) Blocker bonus (new, e.g., for AA)
    if props['rank_counts'].get(ranks_str.index('A'), 0) >= 2:
        score += 5
        score_breakdown.append(("Ace Blocker Bonus", "+5"))
    
    # --- 4. Tier Assignment (adjusted thresholds) ---
    if score >= 80:
        return 1, "Elite - A top-tier hand with immense nut potential, combining high pairs, suitedness, and connectivity.", score_breakdown, score
    elif score >= 65:
        return 2, "Premium - A very strong hand with excellent coordination, often featuring suited high pairs or powerful rundowns.", score_breakdown, score
    elif score >= 45:
        return 3, "Strong - A solid, profitable hand with good suited and/or connected components. Playable in most positions.", score_breakdown, score
    elif score >= 25:
        return 4, "Playable - A speculative hand that relies on position and hitting a favorable flop. Best played in late position or multi-way pots.", score_breakdown, score
    else:
        return 5, "Trash/Marginal - A weak hand with poor coordination. Lacks significant pair, suit, or straight potential and should usually be folded.", score_breakdown, score

def get_preflop_suggestion(tier: int, position: str) -> tuple[str, str]:
    """
    Provides a pre-flop action suggestion based on hand tier and position.
    """
    # Default to folding for safety
    action = "Fold"
    reason = "This hand is generally not strong enough to play from this position."

    if tier == 1:
        action = "Raise / 3-Bet"
        reason = "Elite Hand: Always play aggressively. Raise first-in, and 3-bet or 4-bet against other raises to build the pot and isolate opponents."
    elif tier == 2:
        action = "Raise / 3-Bet"
        reason = "Premium Hand: Raise from any position. Consider 3-betting, especially with position, to punish weaker hands."
    elif tier == 3:
        if position in ['CO', 'BTN']:
            action = "Raise"
            reason = "Strong Hand: Open-raise from late position. It has good playability but benefits greatly from having position post-flop."
        elif position in ['HJ', 'BB']:
            action = "Call / Raise"
            reason = "Strong Hand: Can be opened from Hijack. From the Big Blind, it's a profitable call against a single raise. Play cautiously without position."
        else: # UTG, SB
            action = "Fold"
            reason = "Strong Hand: Out of position, this hand can be dominated. It's often best to fold from early position or the Small Blind unless the table is very passive."
    elif tier == 4:
        if position == 'BTN':
            action = "Raise"
            reason = "Playable Hand: Best played as an open-raise from the Button when folded to you. Requires position to be profitable."
        elif position == 'BB':
            action = "Call / Check"
            reason = "Playable Hand: Can be defended from the Big Blind against a single raise, especially if closing the action multi-way. Play post-flop with caution."
        else: # UTG, HJ, CO, SB
            action = "Fold"
            reason = "Playable Hand: Too speculative to play from early or middle position. Lacks the raw strength to be profitable without maximum positional advantage."
    elif tier == 5:
        action = "Fold"
        reason = "Trash/Marginal Hand: This hand has poor coordination and should be folded from all positions to avoid difficult and unprofitable post-flop spots."

    return action, reason

@hand_eval_bp.route('/tables')
def tables():
    """Renders the PLO Preflop Ranges article from a Markdown file."""
    try:
        project_root = os.path.abspath(os.path.join(current_app.root_path, '..', '..'))
        md_path = os.path.join(project_root, 'resources', 'articles', 'markdown', 'Pot Limit Omaha (PLO) Preflop Ranges in a 6-Max Table.md')
        
        with open(md_path, 'r', encoding='utf-8') as f:
            content_md = f.read()
        
        content_html = markdown.markdown(content_md, extensions=['tables'])
        title = "PLO Pre-flop Ranges"
        subtitle = "A guide to pre-flop starting hand ranges in 6-Max Pot Limit Omaha."
    except FileNotFoundError:
        flash("The article file could not be found.", "danger")
        content_html = "<p>Sorry, the article content is currently unavailable.</p>"
        title, subtitle = "Article Not Found", ""
    
    return render_template('plo_hand_strength_article.html', title=title, subtitle=subtitle, content=content_html)

@hand_eval_bp.route('/plo_hand_form')
def plo_hand_form():
    """PLO Hand Form page route"""
    button_form = ButtonPositionForm()
    hand_form = HandForm()
    button_position = session.get('button_position', 1)  # Default to 1
    return render_template('plo_hand_form.html', title='PLO Hand Form', button_position=button_position, button_form=button_form, hand_form=hand_form)

@hand_eval_bp.route('/switch_button_position', methods=['POST'])
def switch_button_position():
    """Updates the button position in the session."""
    button_form = ButtonPositionForm()
    if button_form.validate_on_submit():
        session['button_position'] = request.form.get('button_position', 1, type=int)
    return redirect(url_for('hand_eval.plo_hand_form'))

@hand_eval_bp.route('/hand_details', methods=['POST', 'GET'])
def submit_form():
    """Handles form submission and processes data."""
    button_form = ButtonPositionForm()
    hand_form = HandForm()
    button_position = session.get('button_position', 1)

    # If it's a GET request and we have data, show the details page.
    if request.method == 'GET' and 'form_data' in session:
        return render_template('hand_details.html', form_data=session['form_data'])

    # If it's a POST request (form submission), validate and process.
    if hand_form.validate_on_submit():
        logging.debug(f"Request form data: {request.form}")
        form_data = algo.process_hand_data(request.form, button_position)  # Assuming this is the full line; replace truncated part if needed
        session['form_data'] = form_data
        return redirect(url_for('hand_eval.submit_form'))  # Redirect to GET to show details

    return render_template('plo_hand_form.html', title='PLO Hand Form', button_position=button_position, button_form=button_form, hand_form=hand_form)

@hand_eval_bp.route('/hand_evaluation')
def hand_evaluation():
    """Renders the detailed hand evaluation page."""
    if 'form_data' not in session:
        flash("No hand data available to evaluate. Please set up a new hand.", "warning")
        return redirect(url_for('hand_eval.plo_hand_form'))
    
    return render_template('hand_evaluation.html', form_data=session['form_data'])

def load_plo_hand_rankings_data(app):
    """Preloads the large CSV into a Pandas DataFrame at app startup."""
    sorted_csv_path = os.path.join(app.root_path, 'data', 'plo_hands_evaluated_sorted.csv')
    original_csv_path = os.path.join(app.root_path, 'data', 'plo_hands_evaluated.csv')
    
    csv_path = sorted_csv_path
    if not os.path.exists(sorted_csv_path):
        app.logger.warning(f"Sorted CSV not found at {sorted_csv_path}. Falling back to original file.")
        csv_path = original_csv_path

    try:
        # Use the pre-sorted CSV file
        # csv_path is now determined above
        df = pd.read_csv(csv_path, low_memory=False)  # low_memory=False for large files
        
        # Log the actual columns found in the CSV
        app.logger.info(f"Original CSV columns: {list(df.columns)}")
        
        # Create a mapping for flexible column renaming
        column_mapping = {}
        for col in df.columns:
            col_lower = col.lower().strip()
            if col_lower in ['cards', 'hand']:
                column_mapping[col] = 'Hand'
            elif col_lower in ['rating', 'tier']:
                column_mapping[col] = 'Tier'
            elif col_lower in ['score', 'rating score', 'rating_score', 'strength']:
                column_mapping[col] = 'Rating Score'
            elif col_lower in ['reason', 'rating reason', 'rating_reason', 'description']:
                column_mapping[col] = 'Rating Reason'
        
        # Apply the mapping
        df = df.rename(columns=column_mapping)
        app.logger.info(f"Renamed columns: {list(df.columns)}")
        
        # Ensure Rating Score is numeric
        df['Rating Score'] = pd.to_numeric(df['Rating Score'], errors='coerce')
        
        # Check if Tier column exists and has valid data
        if 'Tier' not in df.columns or df['Tier'].isna().all():
            app.logger.info("Tier column missing or empty - calculating from Rating Score")
            # Calculate tier based on Rating Score using the same logic as evaluate_hand_strength
            def score_to_tier(score):
                if pd.isna(score):
                    return 5
                elif score >= 85:
                    return 1
                elif score >= 70:
                    return 2
                elif score >= 50:
                    return 3
                elif score >= 30:
                    return 4
                else:
                    return 5
            
            df['Tier'] = df['Rating Score'].apply(score_to_tier)
            app.logger.info("Successfully calculated Tier from Rating Score")
        else:
            # Try to convert text-based ratings to numeric tiers
            rating_to_tier = {
                'Elite+': 1,
                'Elite': 1,
                'Premium': 2,
                'Strong': 3,
                'Playable': 4,
                'Marginal': 5,
                'Trash': 5,
                '1': 1,
                '2': 2,
                '3': 3,
                '4': 4,
                '5': 5
            }
            
            # First try to convert directly to numeric
            df['Tier'] = pd.to_numeric(df['Tier'], errors='coerce')
            
            # If we have NaN values, try mapping from text
            if df['Tier'].isna().any():
                app.logger.info("Converting text-based ratings to numeric tiers")
                df['Tier_Text'] = df['Tier'].astype(str).str.strip()
                df['Tier'] = df['Tier_Text'].map(rating_to_tier)
                df = df.drop('Tier_Text', axis=1)
                
                # For any remaining NaN, calculate from score
                missing_tiers = df['Tier'].isna()
                if missing_tiers.any():
                    app.logger.info(f"Calculating {missing_tiers.sum()} missing tiers from Rating Score")
                    def score_to_tier(score):
                        if pd.isna(score):
                            return 5
                        elif score >= 85:
                            return 1
                        elif score >= 70:
                            return 2
                        elif score >= 50:
                            return 3
                        elif score >= 30:
                            return 4
                        else:
                            return 5
                    df.loc[missing_tiers, 'Tier'] = df.loc[missing_tiers, 'Rating Score'].apply(score_to_tier)
        
        # Add tier-based descriptions for Rating Reason
        tier_reasons = {
            1: "Elite - A top-tier hand with immense nut potential",
            2: "Premium - A very strong hand with excellent coordination",
            3: "Strong - A solid, profitable hand",
            4: "Playable - A speculative hand best played with position",
            5: "Trash/Marginal - A weak hand with poor coordination"
        }
        
        if 'Rating Reason' not in df.columns:
            df['Rating Reason'] = df['Tier'].map(tier_reasons).fillna("Unrated hand")
            app.logger.info("Added 'Rating Reason' column with default values")
        else:
            # Fill in missing reasons based on tier
            df['Rating Reason'] = df['Rating Reason'].fillna(df['Tier'].map(tier_reasons))
        
        # Verify required columns exist
        required_cols = ['Hand', 'Tier', 'Rating Score']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            app.logger.error(f"Missing required columns after renaming: {missing_cols}")
            app.logger.error(f"Available columns: {list(df.columns)}")
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        # Clean up Hand column - remove commas
        df['Hand'] = df['Hand'].str.replace(',', '')
        
        # Create a new column with only the sorted ranks for flexible searching
        # e.g., 'AsAdKsKd' -> 'AAKK'
        df['RanksOnly'] = df['Hand'].apply(lambda h: "".join(sorted([c for i, c in enumerate(h) if i % 2 == 0], key=lambda r: "AKQJT98765432".index(r.upper()))))
        app.logger.info("Successfully created 'RanksOnly' column for searching.")

        # Drop rows with invalid data
        rows_before = len(df)
        df = df.dropna(subset=['Tier', 'Rating Score'])
        rows_after = len(df)
        if rows_before != rows_after:
            app.logger.warning(f"Dropped {rows_before - rows_after} rows with invalid data")
        
        app.config['PLO_HAND_DF'] = df
        app.logger.info(f"Successfully loaded PLO hand data from {csv_path} ({len(df)} rows)")
    except FileNotFoundError:
        app.logger.error(f"CSV file not found at {csv_path}")
    except pd.errors.ParserError:
        app.logger.error(f"Error parsing CSV at {csv_path}")
    except Exception as e:
        app.logger.error(f"Unexpected error loading PLO hand data: {e}")

# Added: Preload function for optimization
def sort_hand_string(hand_str):
    """
    Sorts a 4-card hand string (e.g., '4sAcKd5d') by rank in descending order and then by suit.
    This function is a copy of the one in scripts/sort_hand_data.py, adapted for Flask logging.
    """
    rank_order = "AKQJT98765432"
    suit_order = "shdc" # Spades > Hearts > Diamonds > Clubs

    if not isinstance(hand_str, str):
        return hand_str  # Return as is if not a string

    # Clean the hand string by removing commas and spaces
    cleaned_hand_str = hand_str.replace(',', '').replace(' ', '')

    # Validate length after cleaning
    if len(cleaned_hand_str) % 2 != 0:
        current_app.logger.debug(f"Partial hand string '{cleaned_hand_str}' has odd length, not sorting.")
        return hand_str # Return original if length is odd, as it's an incomplete card

    cards = [cleaned_hand_str[i:i+2] for i in range(0, len(cleaned_hand_str), 2)]

    try:
        sorted_cards = sorted(cards, key=lambda card: (rank_order.index(card[0].upper()), suit_order.index(card[1].lower())))
    except ValueError as e:
        current_app.logger.warning(f"Could not sort hand '{hand_str}'. Invalid character found. Error: {e}")
        return hand_str

    return "".join(sorted_cards)

def _pretty_print_hand(hand_str):
    """Formats a hand string (e.g., 'AsKsQhJh') with HTML for suit symbols and colors."""
    # Add a check to handle potential None or empty strings from the data
    if not hand_str or not isinstance(hand_str, str) or len(hand_str) % 2 != 0:
        return ""

    suit_symbols = {'s': '♠', 'h': '♥', 'd': '♦', 'c': '♣'}
    hand = ''
    for i in range(0, len(hand_str), 2):
        rank = hand_str[i]
        suit = hand_str[i+1].lower()
        # Use CSS classes for theming instead of inline styles
        hand += f'<span class="suit-{suit}">{rank}{suit_symbols.get(suit, suit)}</span>'
    return hand

@hand_eval_bp.route('/plo_hand_rankings', methods=['GET', 'POST'])
def plo_hand_rankings():
    if request.method == 'POST':
        try:
            df = current_app.config.get('PLO_HAND_DF')
            if df is None:
                current_app.logger.error('PLO hand data not loaded.')
                return jsonify({'error': 'Hand data not loaded. Check server logs.'}), 500

            # Extract DataTables parameters (form data)
            draw = int(request.form.get('draw', 0))
            start = int(request.form.get('start', 0))
            length = int(request.form.get('length', 25))
            search_value = request.form.get('search[value]', '').strip().lower()
            
            # Apply sorting logic to the search value
            processed_search_value = sort_hand_string(search_value)

            # Ordering
            order_col = int(request.form.get('order[0][column]', 1))  # Default to Tier (column 1)
            order_dir = request.form.get('order[0][dir]', 'asc')

            # --- Smart Filtering ---
            # Check if the search value contains suits (by looking for s, h, d, c)
            contains_suits = any(c in search_value for c in 'shdc')

            # Filter
            if search_value:
                if contains_suits:
                    # If suits are present, search the full hand string
                    processed_search_value = sort_hand_string(search_value)
                    filtered_df = df[df['Hand'].str.lower().str.contains(processed_search_value.lower(), na=False)]
                else:
                    # If no suits, search the RanksOnly column
                    sorted_rank_query = "".join(sorted(search_value.upper(), key=lambda r: "AKQJT98765432".index(r)))
                    filtered_df = df[df['RanksOnly'].str.contains(sorted_rank_query, na=False)]
            else:
                filtered_df = df.copy()

            # Sort
            col_map = {1: 'Tier', 2: 'Rating Score'}
            sort_col = col_map.get(order_col, 'Tier')
            ascending = order_dir == 'asc'
            filtered_df = filtered_df.sort_values(by=sort_col, ascending=ascending)

            # Paginate
            paginated_df = filtered_df.iloc[start:start + length]

            # Format output
            data_out = []
            for _, row in paginated_df.iterrows():
                data_out.append({
                    'Hand': f"<span data-search='{row['Hand']}'>{_pretty_print_hand(row['Hand'])}</span>",
                    'Tier': row['Tier'],
                    'Rating Score': f"{row['Rating Score']:.1f}",
                    'Rating Reason': row['Rating Reason']
                })

            return jsonify({
                'draw': draw,
                'recordsTotal': len(df),
                'recordsFiltered': len(filtered_df),
                'data': data_out
            })
        except KeyError as e:
            current_app.logger.error(f"Missing column in DataFrame: {e}")
            return jsonify({'error': f"Missing column: {e}"}), 500
        except Exception as e:
            current_app.logger.error(f"Error in plo_hand_rankings POST: {e}")
            return jsonify({'error': 'Internal server error'}), 500

    # GET: Render the template
    return render_template('plo_hand_rankings.html', title='PLO Hand Rankings')

@hand_eval_bp.route('/plo-hand-strength-quiz', methods=['GET', 'POST'])
def plo_hand_strength_quiz():
    """PLO Hand Strength Quiz page route."""
    form = HudStatsQuizForm() # Reusing the same form is fine
    if form.validate_on_submit():
        num_questions = int(form.num_questions.data)

        tier_map = {
            1: "Elite",
            2: "Premium",
            3: "Strong",
            4: "Playable",
            5: "Trash/Marginal",
        }

        try:
            # Use the pre-loaded DataFrame which is already cleaned and standardized
            df = current_app.config.get('PLO_HAND_DF')
            if df is None:
                flash("Hand data is not loaded. Cannot create quiz.", "error")
                return redirect(url_for('hand_eval.plo_hand_strength_quiz'))

            # The DataFrame is already processed, so we can use it directly.
            # We just need to ensure the columns are what we expect.
            if 'Hand' not in df.columns or 'Tier' not in df.columns:
                flash("Hand data is missing required 'Hand' or 'Tier' columns.", "error")
                return redirect(url_for('hand_eval.plo_hand_strength_quiz'))

            all_hands = df[['Hand', 'Tier']].rename(columns={'Hand': 'hand', 'Tier': 'tier'}).to_dict('records')

        except FileNotFoundError as e:
            flash(f"Could not load hand strength data. File not found: {e}", "error")
            return redirect(url_for('hand_eval.plo_hand_strength_quiz'))
        except Exception as e:
            flash(f"Error loading data for quiz: {e}", "error")
            return redirect(url_for('hand_eval.plo_hand_strength_quiz'))

        if not all_hands:
            flash("Hand strength data is empty or invalid. Cannot create quiz.", "error")
            return redirect(url_for('hand_eval.plo_hand_strength_quiz'))

        questions = []
        # Get all unique tiers for generating wrong answers
        all_tiers = sorted(list(set(hand['tier'] for hand in all_hands)))

        # Select a random sample of hands for the questions
        sampled_hands = random.sample(all_hands, min(num_questions, len(all_hands)))

        for hand_data in sampled_hands:
            correct_answer_tier = hand_data['tier']
            correct_answer_label = f"{correct_answer_tier} - {tier_map.get(correct_answer_tier, '')}"

            # Generate 3 unique incorrect answers
            possible_wrong_answers = [t for t in all_tiers if t != correct_answer_tier]
            num_wrong_to_select = min(3, len(possible_wrong_answers))
            wrong_answers_tiers = random.sample(possible_wrong_answers, num_wrong_to_select)

            answers = [(str(correct_answer_tier), correct_answer_label)]
            for tier in wrong_answers_tiers:
                answers.append((str(tier), f"{tier} - {tier_map.get(tier, '')}"))

            # Pad with other tiers if there aren't enough unique ones
            while len(answers) < 4:
                padding_choice = random.choice([t for t in all_tiers if t not in [int(a[0]) for a in answers]])
                answers.append((str(padding_choice), f"{padding_choice} - {tier_map.get(padding_choice, '')}"))

            random.shuffle(answers)

            questions.append({
                'question': hand_data['hand'], # The hand string is the question
                'answers': answers, # List of (value, label) tuples
                'correct_answer': str(correct_answer_tier),
                'is_hand_strength_quiz': True # Flag for the template
            })

        session['quiz_questions'] = questions
        session['current_question'] = 0
        session['score'] = 0
        session['incorrect_answers'] = []

        return redirect(url_for('hand_eval.quiz'))
    
    # If it's a GET request or validation fails, render the form page
    return render_template('plo_hand_strength_quiz.html', title='PLO Hand Strength Quiz', form=form)


class HudStatsQuizForm(FlaskForm):
    """Form for starting the HUD stats quiz."""
    num_questions = SelectField(
        'Number of Questions',
        choices=[('1', '1'), ('5', '5'), ('10', '10'), ('20', '20')],
        validators=[DataRequired()],
        default='5'
    )
    submit = SubmitField('Start Quiz')


class QuizAnswerForm(FlaskForm):
    """Form for answering a quiz question."""
    answer = RadioField('Answer', validators=[DataRequired()])
    submit = SubmitField('Submit Answer')



@hand_eval_bp.route('/hud-stats-quiz', methods=['GET', 'POST'])
def hud_stats_quiz():
    """HUD Stats Quiz page route, handles both displaying the form and starting the quiz."""
    form = HudStatsQuizForm()
    if form.validate_on_submit():
        num_questions = int(form.num_questions.data)
        try:
            with current_app.open_resource('data/hud_player_types.json', 'r') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            flash(f"Could not load HUD player type data: {e}", "error")
            return redirect(url_for('hand_eval.hud_stats_quiz'))

        questions = []
        player_types = data['player_types']
        stats = data['stats']

        for _ in range(num_questions):
            stat = random.choice(stats)
            player_type = random.choice(player_types)
            correct_answer = stat['values'][player_type['name']]

            answers = [correct_answer]
            while len(answers) < 4:
                random_stat = random.choice(stats)
                random_player_type = random.choice(player_types)
                random_answer = random_stat['values'][random_player_type['name']]
                if random_answer not in answers:
                    answers.append(random_answer)
            
            random.shuffle(answers)

            questions.append({
                'question': f"What is the typical {stat['name']} of a {player_type['name']}?",
                'answers': answers,
                'correct_answer': correct_answer
            })

        session['quiz_questions'] = questions
        session['current_question'] = 0
        session['score'] = 0
        session['incorrect_answers'] = []

        return redirect(url_for('hand_eval.quiz'))
    
    # If it's a GET request or validation fails, render the form page
    return render_template('hud_stats_quiz.html', title='HUD Stats Quiz', form=form)





    questions = []
    player_types = data['player_types']
    stats = data['stats']

    for _ in range(num_questions):
        stat = random.choice(stats)
        player_type = random.choice(player_types)
        correct_answer = stat['values'][player_type['name']]

        answers = [correct_answer]
        while len(answers) < 4:
            random_stat = random.choice(stats)
            random_player_type = random.choice(player_types)
            random_answer = random_stat['values'][random_player_type['name']]
            if random_answer not in answers:
                answers.append(random_answer)
        
        random.shuffle(answers)

        questions.append({
            'question': f"What is the typical {stat['name']} of a {player_type['name']}?",
            'answers': answers,
            'correct_answer': correct_answer
        })

    session['quiz_questions'] = questions
    session['current_question'] = 0
    session['score'] = 0

    return redirect(url_for('hand_eval.quiz'))

@hand_eval_bp.route('/quiz', methods=['GET', 'POST'])
def quiz():
    """Displays the current quiz question and handles answer submission."""
    if 'quiz_questions' not in session:
        return redirect(url_for('hand_eval.hud_stats_quiz'))

    current_question_index = session.get('current_question', 0)
    questions = session.get('quiz_questions', [])

    if current_question_index >= len(questions):
        return redirect(url_for('hand_eval.quiz_results'))

    question = questions[current_question_index]
    form = QuizAnswerForm()
    form.answer.choices = question['answers']

    if form.validate_on_submit():
        user_answer = form.answer.data
        if str(question['correct_answer']) == user_answer:
            session['score'] = session.get('score', 0) + 1
        else:
            is_hand_quiz = question.get('is_hand_strength_quiz', False)
            incorrect = {
                'question': question['question'],
                'your_answer': user_answer,
                'correct_answer': question['correct_answer'],
                'is_hand_strength_quiz': is_hand_quiz
            }
            session['incorrect_answers'].append(incorrect)
        session['current_question'] = current_question_index + 1
        return redirect(url_for('hand_eval.quiz'))

    # Prepare the question for display (render hand images if needed)
    question_display = _pretty_print_hand(question['question']) if question.get('is_hand_strength_quiz') else question['question']

    return render_template(
        'quiz.html',
        title='HUD Stats Quiz',
        question=question,
        form=form,
        question_number=current_question_index + 1,
        total_questions=len(questions),
        question_display=question_display
    )




@hand_eval_bp.route('/quiz-results')
def quiz_results():
    """Displays the quiz results."""
    if 'quiz_questions' not in session:
        return redirect(url_for('hand_eval.hud_stats_quiz'))

    score = session.get('score', 0)
    questions = session.get('quiz_questions', [])
    total_questions = len(questions)
    percentage = (score / total_questions) * 100 if total_questions > 0 else 0

    # Determine which quiz was taken to set the correct 'Try Again' link
    quiz_type = 'hud_stats' # default
    if questions and questions[0].get('is_hand_strength_quiz'):
        quiz_type = 'plo_hand_strength'


    ratings = [
        {'name': 'Crusher', 'icon': 'bi-star-fill', 'min_score': 90},
        {'name': 'High Roller', 'icon': 'bi-gem', 'min_score': 80},
        {'name': 'Shark', 'icon': 'bi-trophy', 'min_score': 70},
        {'name': 'Winning Player', 'icon': 'bi-graph-up', 'min_score': 60},
        {'name': 'Grinder', 'icon': 'bi-hammer', 'min_score': 50},
        {'name': 'TAGfish', 'icon': 'bi-cone-striped', 'min_score': 40},
        {'name': 'Calling Station', 'icon': 'bi-telephone', 'min_score': 30},
        {'name': 'Gambler', 'icon': 'bi-dice-5', 'min_score': 20},
        {'name': 'Fish', 'icon': 'bi-water', 'min_score': 10},
        {'name': 'Donk', 'icon': 'bi-question-circle', 'min_score': 0}
    ]

    user_rating = ratings[-1]  # Default to the lowest rating
    for r in ratings:
        if percentage >= r['min_score']:
            user_rating = r
            break

    tier_map = {
        1: "Elite",
        2: "Premium",
        3: "Strong",
        4: "Playable",
        5: "Trash/Marginal"
    }

    incorrect_answers = session.get('incorrect_answers', [])
    
    # Prepare incorrect answers for display with card images
    for item in incorrect_answers:
        if 'is_hand_strength_quiz' in item and item['is_hand_strength_quiz']:
            item['question_display'] = _pretty_print_hand(item['question'])
            # Ensure the answer is an integer before looking it up in the map
            try:
                your_answer_tier = int(item['your_answer'])
                correct_answer_tier = int(item['correct_answer'])
                item['your_answer_display'] = f"{your_answer_tier} ({tier_map.get(your_answer_tier, '')})"
                item['correct_answer_display'] = f"{correct_answer_tier} ({tier_map.get(correct_answer_tier, '')})"
            except (ValueError, TypeError):
                 item['your_answer_display'] = item['your_answer']
                 item['correct_answer_display'] = item['correct_answer']
        else:
            item['question_display'] = item['question']
            item['your_answer_display'] = item['your_answer']
            item['correct_answer_display'] = item['correct_answer']

    return render_template(
        'quiz_results.html',
        title='Quiz Results',
        score=score,
        total_questions=total_questions,
        percentage=percentage,
        rating=user_rating,
        incorrect_answers=incorrect_answers,
        quiz_type=quiz_type
    )

@hand_eval_bp.route('/hud-player-type-guide')
def hud_player_type_guide():
    try:
        json_path = os.path.join(current_app.root_path, 'data', 'hud_player_types.json')
        current_app.logger.debug(f"Attempting to load JSON from: {json_path}")
        with open(json_path, 'r') as f:
            data = json.load(f)
        current_app.logger.debug(f"Loaded HUD data: {data}")
        # Verify data structure
        if not data.get('player_types') or not data.get('stats') or not all(stat.get('values') for stat in data.get('stats', [])):
            current_app.logger.error("Incomplete HUD data: missing player_types, stats, or values")
            flash('Error: Incomplete HUD data.', 'danger')
            data = {"player_types": [], "stats": []}
    except FileNotFoundError as e:
        current_app.logger.error(f"HUD JSON file not found: {e}")
        flash('Error: HUD data file not found.', 'danger')
        data = {"player_types": [], "stats": []}
    except json.JSONDecodeError as e:
        current_app.logger.error(f"Invalid JSON in HUD data file: {e}")
        flash('Error: Invalid HUD data format.', 'danger')
        data = {"player_types": [], "stats": []}
    except Exception as e:
        current_app.logger.error(f"Unexpected error loading HUD data: {e}")
        flash('Error loading HUD data.', 'danger')
        data = {"player_types": [], "stats": []}
    return render_template('hud_player_type.html', data=data)

@hand_eval_bp.route('/spr-strategy')
def spr_strategy():
    """Renders the SPR strategy guide page."""
    return render_template('spr_strategy.html', title='SPR Strategy Guide')

@hand_eval_bp.route('/plo-hand-strength-article')
def plo_hand_strength_article():
    """Renders the PLO hand strength article from a Markdown file."""
    try:
        # The path is relative to the project root, so we construct it carefully.
        # Assuming the 'resources' directory is at the same level as 'src'.
        project_root = os.path.abspath(os.path.join(current_app.root_path, '..', '..'))
        md_path = os.path.join(project_root, 'resources', 'articles', 'markdown', 'PLO Starting Hand Rankings by Classification.md')
        
        with open(md_path, 'r', encoding='utf-8') as f:
            content_md = f.read()
        
        content_html = markdown.markdown(content_md, extensions=['tables'])
    except FileNotFoundError:
        flash("The article file could not be found.", "danger")
        content_html = "<p>Sorry, the article content is currently unavailable.</p>"
    
    return render_template('plo_hand_strength_article.html', title='PLO Starting Hand Strength', content=content_html)
@hand_eval_bp.route('/player-color-scheme-guide')
def player_color_scheme_guide():
    """Renders the player color scheme guide page."""
    return render_template('player_color_scheme.html', title='Player Color Scheme Guide')