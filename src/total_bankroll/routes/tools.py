import json
import os
import re
import html
from flask import Blueprint, render_template, request, current_app, flash
from flask_security import current_user, login_required, login_required
from decimal import Decimal, InvalidOperation
import math
from flask_wtf import FlaskForm
from wtforms import DecimalField, SubmitField
from wtforms.validators import DataRequired, NumberRange
from ..utils import get_user_bankroll_data
from ..recommendations import RecommendationEngine
import logging

logging.basicConfig(level=logging.DEBUG)

tools_bp = Blueprint('tools', __name__)

class BankrollGoalsForm(FlaskForm):
    """Form for the Bankroll Goals Calculator."""
    target_bankroll = DecimalField('Target Bankroll', validators=[DataRequired(), NumberRange(min=0.01, message="Target must be greater than zero.")])
    monthly_profit = DecimalField('Expected Monthly Profit / Contribution', validators=[DataRequired(), NumberRange(min=0.01, message="Monthly profit must be greater than zero.")])
    submit = SubmitField('Calculate Goal')

class SPRCalculatorForm(FlaskForm):
    effective_stack = DecimalField('Effective Stack Size', validators=[DataRequired(), NumberRange(min=0)])
    pot_size = DecimalField('Pot Size', validators=[DataRequired(), NumberRange(min=0.01, message="Pot size must be greater than zero.")])
    submit = SubmitField('Calculate SPR')

def parse_currency_to_decimal(currency_str):
    """Helper to parse currency string to Decimal."""
    return Decimal(str(currency_str).replace('$', '').replace(',', ''))

@tools_bp.route('/tools')
@login_required
def tools_page():
    return render_template('tools.html')

def _get_user_selections(request_args):
    """Extracts and maps user filter selections from request arguments."""
    game_type_map = {
        'limit_holdem': "Limit Hold’Em",
        'nlhe': "NLHE",
        'plo': "PLO",
        'na': "NA"
    }
    skill_level_map = {
        'soft': "Soft Games",
        'tough': "Tough Games",
        'na': "NA"
    }
    risk_tolerance_map = {
        'conservative': "Conservative",
        'aggressive': "Aggressive",
        'na': "NA"
    }
    game_environment_map = {
        'live': "Live Poker",
        'online': "Online Poker",
        'na': "NA"
    }
    return {
        'game_type': game_type_map.get(request_args.get('game_type', 'nlhe')),
        'skill_level': skill_level_map.get(request_args.get('skill_level', 'tough')),
        'risk_tolerance': risk_tolerance_map.get(request_args.get('risk_tolerance', 'conservative')),
        'game_environment': game_environment_map.get(request_args.get('game_environment', 'online'))
    }

@tools_bp.route('/poker_stakes')
@login_required
def poker_stakes_page():
    # Get user selections and bankroll
    selections = _get_user_selections(request.args)
    bankroll_data = get_user_bankroll_data(current_user.id)
    total_bankroll = bankroll_data['total_bankroll']
    
    # Initialize the recommendation engine
    engine = RecommendationEngine()
    range_data = engine._calculate_weighted_range(selections, 'cash_games')
    buy_in_multiple = range_data['average_multiple']

    # Load cash game stakes data from JSON
    cash_stakes_json_path = os.path.join(current_app.root_path, 'data', 'cash_game_stakes.json')
    with open(cash_stakes_json_path, 'r') as f:
        cash_stakes_data = json.load(f)
    stakes_list = cash_stakes_data['stakes']

    # Calculate all recommendation messages
    recommendations = engine.get_cash_game_recommendation_data(selections, total_bankroll, stakes_list)
    recommended_stake_index = recommendations['recommended_stake_index']

    # Reconstruct the table in the list-of-lists format expected by the template
    headers = ["Small Blind", "Big Blind", "Minimum Buy-In", "Maximum Buy-In", "Bankroll Required", "Additional $ Required"]
    cash_stakes_table = [headers]
    for i, stake in enumerate(stakes_list):
        max_buy_in = parse_currency_to_decimal(stake['max_buy_in'])

        bankroll_required = Decimal('0.0')
        if buy_in_multiple > 0:
            bankroll_required = max_buy_in * buy_in_multiple

        additional_required = bankroll_required - total_bankroll

        # For stakes lower than recommended, show the negative "additional required" to indicate the buffer.
        # For the recommended stake and higher, clamp to zero if the user is already rolled.
        if recommended_stake_index != -1 and i < recommended_stake_index:
            pass  # Keep the negative value for stakes below the recommended one
        elif additional_required < 0:
            additional_required = Decimal('0.0')

        cash_stakes_table.append([
            stake['small_blind'],
            stake['big_blind'],
            stake['min_buy_in'],
            stake['max_buy_in'],
            f"${bankroll_required:,.2f}",
            f"${additional_required:,.2f}"
        ])

    return render_template(
        'poker_stakes.html',
        total_bankroll=total_bankroll,
        cash_stakes_table=cash_stakes_table,
        **recommendations,
        bankroll_recommendation=range_data['recommendation_string'],
        # Pass filter values to template
        game_type=request.args.get('game_type', 'nlhe'),
        skill_level=request.args.get('skill_level', 'tough'),
        risk_tolerance=request.args.get('risk_tolerance', 'conservative'),
        game_environment=request.args.get('game_environment', 'online')
    )

@tools_bp.route('/tournament_stakes')
@login_required
def tournament_stakes_page():
    """Tournament Stakes page."""
    selections = _get_user_selections(request.args)
    site_filter = request.args.get('site_filter', 'all')
    
    # Initialize the recommendation engine
    engine = RecommendationEngine()

    # Load tournament buy-in data from JSON
    json_path = os.path.join(current_app.root_path, 'data', 'tournament_buy_ins.json')
    with open(json_path, 'r') as f:
        tournament_buy_ins = json.load(f)

    # Calculate range and mean buy-ins
    range_data = engine._calculate_weighted_range(selections, 'tournaments')
    mean_buy_ins = range_data['average_multiple']

    bankroll_data = get_user_bankroll_data(current_user.id)
    total_bankroll = bankroll_data['total_bankroll']

    # --- Add new columns to tournament_buy_ins data ---
    for site_key, site_data in tournament_buy_ins.items():
        if 'buy_ins' in site_data:
            for item in site_data['buy_ins']:
                buy_in_str = item.get('buy_in')
                if not buy_in_str:
                    item['bankroll_required'] = '$0.00'
                    item['additional_required'] = '$0.00'
                    item['buy_in_dec'] = Decimal('0.0')
                    continue
                
                try:
                    buy_in_dec = parse_currency_to_decimal(buy_in_str)
                    item['buy_in_dec'] = buy_in_dec
                    
                    bankroll_required = Decimal('0.0')
                    if mean_buy_ins > 0:
                        bankroll_required = buy_in_dec * mean_buy_ins
                    
                    additional_required = bankroll_required - total_bankroll
                    if additional_required < 0:
                        additional_required = Decimal('0.0')
                    
                    item['bankroll_required'] = f"${bankroll_required:,.2f}"
                    item['additional_required'] = f"${additional_required:,.2f}"
                except (ValueError, InvalidOperation):
                    item['bankroll_required'] = 'N/A'
                    item['additional_required'] = 'N/A'
                    item['buy_in_dec'] = None

    # --- Calculate recommendations and display columns ---
    # First, calculate per-site recommendations to determine the recommended stake for each table.
    for site_key, site_data in tournament_buy_ins.items():
        if 'buy_ins' in site_data:
            # Pass 1: Populate 'buy_in_dec' and build a map for the recommendation engine.
            site_buyins_map = {}
            for item in site_data['buy_ins']:
                buy_in_str = item.get('buy_in')
                if not buy_in_str:
                    item['buy_in_dec'] = Decimal('0.0')
                    continue
                try:
                    buy_in_dec = parse_currency_to_decimal(buy_in_str)
                    item['buy_in_dec'] = buy_in_dec
                    if buy_in_dec not in site_buyins_map:
                        site_buyins_map[buy_in_dec] = buy_in_str
                except (ValueError, InvalidOperation):
                    item['buy_in_dec'] = None
            
            # Calculate the recommendation for this specific site.
            site_recommendations = engine.get_tournament_recommendation_data(selections, total_bankroll, site_buyins_map)
            site_data['recommendations'] = site_recommendations
            recommended_stake_dec = site_recommendations.get('recommended_tournament_stake_dec')

            # Pass 2: Populate the display columns ('Bankroll Required', 'Additional $ Required')
            # using the per-site recommendation to apply the correct logic.
            for item in site_data['buy_ins']:
                buy_in_dec = item.get('buy_in_dec')
                if buy_in_dec is None:
                    item['bankroll_required'] = 'N/A'
                    item['additional_required'] = 'N/A'
                    continue

                bankroll_required = buy_in_dec * mean_buy_ins if mean_buy_ins > 0 else Decimal('0.0')
                additional_required = bankroll_required - total_bankroll

                # For stakes lower than recommended, show the negative "additional required"
                # to indicate the buffer. For higher stakes, clamp to zero.
                if recommended_stake_dec is not None and buy_in_dec < recommended_stake_dec:
                    pass  # Keep the negative value
                elif additional_required < 0:
                    additional_required = Decimal('0.0')

                item['bankroll_required'] = f"${bankroll_required:,.2f}"
                item['additional_required'] = f"${additional_required:,.2f}"

    # --- Calculate Global Recommendation for top messages ---
    # This uses all sites if filter is 'all', or the specific site if filtered.
    global_buyins_map = {}
    sites_to_process_for_global = {}
    if site_filter == 'all':
        sites_to_process_for_global = tournament_buy_ins
    elif site_filter in tournament_buy_ins:
        sites_to_process_for_global = {site_filter: tournament_buy_ins[site_filter]}

    for site_data in sites_to_process_for_global.values():
        for item in site_data.get('buy_ins', []):
            buy_in_dec = item.get('buy_in_dec')
            buy_in_str = item.get('buy_in')
            if buy_in_dec is not None and buy_in_str is not None and buy_in_dec not in global_buyins_map:
                global_buyins_map[buy_in_dec] = buy_in_str

    # Calculate recommendations using the new engine
    global_recommendations = engine.get_tournament_recommendation_data(
        selections, total_bankroll, global_buyins_map
    )

    return render_template('tournament_stakes.html',
                           total_bankroll=total_bankroll,
                           game_type=request.args.get('game_type', 'nlhe'),
                           skill_level=request.args.get('skill_level', 'tough'),
                           risk_tolerance=request.args.get('risk_tolerance', 'conservative'),
                           game_environment=request.args.get('game_environment', 'online'),
                           tournament_bankroll_recommendation=range_data['recommendation_string'],
                           **global_recommendations,
                           site_filter=site_filter,
                           tournament_buy_ins=tournament_buy_ins
                           )

@tools_bp.route('/tools/spr-calculator', methods=['GET', 'POST'])
@login_required
def spr_calculator_page():
    """
    Renders the SPR Calculator page and handles the calculation.
    """
    form = SPRCalculatorForm()
    spr = None
    spr_decision_category = None
    spr_decision_territory = None
    spr_detailed_decisions = None
    spr_detailed_category_header = None

    # Load SPR decision data from decisions.html
    decisions_html_path = os.path.join(current_app.root_path, 'templates', 'decisions.html')
    
    # Data for the summary (Category and Territory)
    spr_summary_table = []
    # Data for the detailed decision table
    spr_detailed_chart_headers = []
    spr_detailed_chart_data = []

    try:
        with open(decisions_html_path, 'r') as f:
            content = f.read()
            logging.debug(f"Loaded decisions.html content length: {len(content)}")
            
            # --- Parse the summary table (SPR, Category, Category 2) ---
            summary_rows = re.findall(
                r'<tr class="category-(?:ultra-low|low|mid|high)">\s*'
                r'<td[^>]*sdval="([\d.]+)"[^>]*>.*?</td>\s*' # Group 1: SPR value from sdval
                r'<td[^>]*>.*?</td>\s*' # Skip Equity
                r'<td[^>]*>.*?</td>\s*' # Skip Pot-Sized Bets
                r'<td[^>]*data-sheets-value="{[^}]*&quot;2&quot;:\s*&quot;([^&]+)&quot;}"[^>]*>.*?</td>\s*' # Group 2: Category
                r'<td[^>]*data-sheets-value="{[^}]*&quot;2&quot;:\s*&quot;([^&]+)&quot;}"[^>]*>.*?</td>\s*' # Group 3: Category 2
                r'</tr>',
                content, re.DOTALL
            )
            logging.debug(f"Found {len(summary_rows)} summary rows.")
            for row in summary_rows:
                try:
                    spr_val = float(row[0]) # row[0] is now directly the sdval
                    category = row[1].strip() # row[1] is now directly the category from data-sheets-value
                    category2 = row[2].strip() # row[2] is now directly the category2 from data-sheets-value
                    spr_summary_table.append({
                        'spr': spr_val,
                        'category': category,
                        'category2': category2
                    })
                except ValueError:
                    if row[0] == '>13': # Check if sdval was '>13' (though regex should prevent this for float)
                        spr_summary_table.append({
                            'spr': float('inf'),
                            'category': row[1].strip(),
                            'category2': row[2].strip()
                        })
                    else:
                        current_app.logger.warning(f"Could not parse SPR summary row: {row}")
            spr_summary_table.sort(key=lambda x: x['spr'])
            logging.debug(f"Parsed spr_summary_table: {spr_summary_table}")

            # --- Parse the detailed decision table (Hand Type and SPR ranges) ---
            detailed_table_match = re.search(r'<table class="table table-bordered table-striped table-custom".*?>(.*?)</table>', content, re.DOTALL)
            if detailed_table_match:
                table_content = detailed_table_match.group(1)
                logging.debug(f"Found detailed table content length: {len(table_content)}")
                
                # Extract header row
                header_row_match = re.search(r'<thead[^>]*>.*?<tr>(.*?)</tr>.*?</thead>', table_content, re.DOTALL)
                if header_row_match:
                    header_cells = re.findall(r'<th[^>]*>(.*?)</th>', header_row_match.group(1))
                    spr_detailed_chart_headers = [html.unescape(re.sub(r'<.*?>', '', h)).strip() for h in header_cells]
                    logging.debug(f"Parsed spr_detailed_chart_headers: {spr_detailed_chart_headers}")

                # Extract data rows
                body_rows = re.findall(r'<tr[^>]*>(.*?)</tr>', table_content.split('<tbody>')[1].split('</tbody>')[0], re.DOTALL)
                for row_content in body_rows:
                    row_cells_data = []
                    # Find all <th> or <td> tags and capture their class and content
                    cell_matches = re.findall(r'<(?:th|td)(?: class="(table-(?:success|warning|danger))")?[^>]*>(.*?)</(?:th|td)>', row_content, re.DOTALL)
                    for class_attr, cell_content in cell_matches:
                        cleaned_content = html.unescape(re.sub(r'<.*?>', '', cell_content)).strip()
                        row_cells_data.append({'content': cleaned_content, 'class': class_attr if class_attr else ''})
                    if row_cells_data:
                        spr_detailed_chart_data.append(row_cells_data)
                logging.debug(f"Parsed spr_detailed_chart_data: {spr_detailed_chart_data}")

    except FileNotFoundError:
        flash("SPR decision data file (decisions.html) not found. Please ensure it exists in the templates directory.", "danger")
        logging.error(f"FileNotFoundError: {decisions_html_path}")
    except Exception as e:
        flash(f"Error loading or parsing SPR decision data: {e}", "danger")
        logging.error(f"Error parsing decisions.html: {e}", exc_info=True)


    if form.validate_on_submit():
        effective_stack = form.effective_stack.data
        pot_size = form.pot_size.data
        try:
            spr = effective_stack / pot_size
            logging.debug(f"Calculated SPR: {spr}")
            
            # --- Determine relevant summary decision ---
            if spr_summary_table:
                relevant_summary_row = None
                for row in spr_summary_table:
                    if spr >= row['spr']:
                        relevant_summary_row = row
                    else:
                        break
                if not relevant_summary_row and spr < spr_summary_table[0]['spr']:
                    relevant_summary_row = spr_summary_table[0]
                elif not relevant_summary_row and spr > spr_summary_table[-1]['spr'] and spr_summary_table[-1]['spr'] != float('inf'):
                    relevant_summary_row = spr_summary_table[-1]

                if relevant_summary_row:
                    spr_decision_category = relevant_summary_row['category']
                    spr_decision_territory = relevant_summary_row['category2']
                    logging.debug(f"Summary Decision: Category={spr_decision_category}, Territory={spr_decision_territory}")
            
            # --- Determine relevant detailed decision column ---
            if spr_detailed_chart_headers and spr_detailed_chart_data:
                # Find the correct header for the calculated SPR
                spr_header_index = -1
                if spr <= 1: spr_detailed_category_header = "SPR ≤ 1 (Ultralow)"
                elif spr <= 4: spr_detailed_category_header = "1 < SPR ≤ 4 (Low)"
                elif spr <= 13: spr_detailed_category_header = "4 < SPR ≤ 13 (Mid)"
                else: spr_detailed_category_header = "SPR > 13 (High)"
                
                try:
                    spr_header_index = spr_detailed_chart_headers.index(spr_detailed_category_header)
                    logging.debug(f"Matched detailed category header: {spr_detailed_category_header} at index {spr_header_index}")
                except ValueError:
                    current_app.logger.warning(f"SPR category header '{spr_detailed_category_header}' not found in detailed chart headers.")

                if spr_header_index != -1:
                    spr_detailed_decisions = []
                    for row_data in spr_detailed_chart_data:
                        if len(row_data) > spr_header_index:
                            spr_detailed_decisions.append({
                                'hand_type': row_data[0]['content'], # First column is Hand Type content
                                'decision': row_data[spr_header_index]['content'], # Decision content
                                'decision_class': row_data[spr_header_index]['class'] # Decision class
                            })
                    logging.debug(f"Filtered spr_detailed_decisions: {spr_detailed_decisions}")

        except InvalidOperation:
            flash("Invalid input for stack or pot size.", "danger")
        except ZeroDivisionError:
            flash("Pot size cannot be zero.", "danger")


    return render_template(
        'spr_calculator.html',
        form=form,
        spr=spr,
        spr_decision_category=spr_decision_category,
        spr_decision_territory=spr_decision_territory,
        spr_detailed_decisions=spr_detailed_decisions,
        spr_detailed_category_header=spr_detailed_category_header
    )

@tools_bp.route('/tools/bankroll-goals', methods=['GET', 'POST'])
@login_required
def bankroll_goals_page():
    """Renders the Bankroll Goals Calculator page and handles calculations."""
    form = BankrollGoalsForm()
    bankroll_data = get_user_bankroll_data(current_user.id)
    current_bankroll = bankroll_data['total_bankroll']
    result = None

    if form.validate_on_submit():
        target_bankroll = form.target_bankroll.data
        monthly_profit = form.monthly_profit.data

        amount_needed = target_bankroll - current_bankroll

        if amount_needed <= 0:
            result = f"Congratulations! Your current bankroll of ${current_bankroll:,.2f} already meets or exceeds your target of ${target_bankroll:,.2f}."
        elif monthly_profit <= 0:
            result = "With a monthly profit of zero or less, you cannot reach your target bankroll. Please enter a positive value."
        else:
            months_needed = math.ceil(amount_needed / monthly_profit)
            years = months_needed // 12
            months = months_needed % 12

            time_str = ""
            if years > 0:
                time_str += f"{years} year{'s' if years > 1 else ''}"
            if months > 0:
                if years > 0:
                    time_str += " and "
                time_str += f"{months} month{'s' if months > 1 else ''}"
            
            if not time_str: # Should not happen with ceil, but as a fallback
                time_str = "less than a month"

            result = (f"To reach your target bankroll of ${target_bankroll:,.2f}, you need to accumulate an additional ${amount_needed:,.2f}. "
                      f"At a rate of ${monthly_profit:,.2f} per month, it will take you approximately {time_str}.")

    return render_template('bankroll_goals.html',
                           form=form,
                           current_bankroll=current_bankroll,
                           result=result)