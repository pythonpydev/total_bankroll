import json
import os
import html
from flask import Blueprint, render_template, request, current_app, flash
from flask_security import current_user, login_required, login_required
from decimal import Decimal, InvalidOperation
import math
from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SubmitField, SelectField, IntegerField
from wtforms.validators import DataRequired, NumberRange, Optional, ValidationError
from ..services import BankrollService, RecommendationService
import logging

# --- Caching for SPR Data ---
_spr_decision_data = None

def get_spr_decision_data():
    """Loads SPR decision data from JSON and caches it."""
    global _spr_decision_data
    if _spr_decision_data is None:
        json_path = os.path.join(current_app.root_path, 'data', 'spr_decisions.json')
        with open(json_path, 'r') as f:
            _spr_decision_data = json.load(f)
    return _spr_decision_data

logging.basicConfig(level=logging.DEBUG)

tools_bp = Blueprint('tools', __name__)

class BankrollGoalsForm(FlaskForm):
    """Form for the Bankroll Goals Calculator."""
    calculation_mode = SelectField('Calculation Type', choices=[('time', 'Calculate Time to Goal'), ('profit', 'Calculate Required Monthly Profit')], default='time')
    target_bankroll = DecimalField('Target Bankroll', validators=[DataRequired(), NumberRange(min=0.01, message="Target must be greater than zero.")])
    monthly_profit = DecimalField('Expected Monthly Profit / Contribution', validators=[Optional(), NumberRange(min=0.01, message="Monthly profit must be greater than zero.")])
    timeframe_months = IntegerField('Timeframe (in months)', validators=[Optional(), NumberRange(min=1, message="Timeframe must be at least 1 month.")])
    submit = SubmitField('Calculate Goal')

    def validate(self, **kwargs):
        if not super().validate(**kwargs):
            return False
        if self.calculation_mode.data == 'time' and self.monthly_profit.data is None:
            self.monthly_profit.errors.append('This field is required for this calculation.')
            return False
        if self.calculation_mode.data == 'profit' and self.timeframe_months.data is None:
            self.timeframe_months.errors.append('This field is required for this calculation.')
            return False
        return True

class SPRCalculatorForm(FlaskForm):
    effective_stack = DecimalField('Effective Stack Size', validators=[DataRequired(), NumberRange(min=0)])
    pot_size = DecimalField('Pot Size', validators=[DataRequired(), NumberRange(min=0.01, message="Pot size must be greater than zero.")])
    submit = SubmitField('Calculate SPR')

class HandStrengthForm(FlaskForm):
    """Form for submitting a hand for strength evaluation."""
    hand = StringField("Enter PLO Hand (e.g., AsKsQhJh)", validators=[DataRequired()], render_kw={"placeholder": "e.g., AsKsQhJh or AA44ds"})
    position = SelectField("Your Position", choices=[('UTG', 'UTG'), ('HJ', 'HJ'), ('CO', 'CO'), ('BTN', 'BTN'), ('SB', 'SB'), ('BB', 'BB')], validators=[DataRequired()])
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
            rank = card[0].upper()
            suit = card[1].lower()
            if rank not in ranks or suit not in suits:
                raise ValidationError(f"Invalid card '{html.escape(card)}'. Use ranks 2-9, T, J, Q, K, A and suits s, h, d, c.")
            if card in seen_cards:
                raise ValidationError(f"Duplicate card '{html.escape(card)}' found in hand.")
            seen_cards.add(card)

def parse_currency_to_decimal(currency_str):
    """Helper to parse currency string to Decimal."""
    return Decimal(str(currency_str).replace('$', '').replace(',', ''))

@tools_bp.route('/tools')
@login_required
def tools_page(): # This function is not being used as intended. The template is rendered directly.
    return render_template('tools/tools.html')

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
    service = BankrollService()
    bankroll_data = service.get_bankroll_breakdown(current_user.id)
    total_bankroll = bankroll_data['total_bankroll']
    
    # Load cash game stakes data from JSON
    cash_stakes_json_path = os.path.join(current_app.root_path, 'data', 'cash_game_stakes.json')
    with open(cash_stakes_json_path, 'r') as f:
        cash_stakes_data = json.load(f)
    stakes_list = cash_stakes_data['stakes']
    
    # Initialize the recommendation service and get recommendations
    rec_service = RecommendationService()
    recommendations = rec_service.get_cash_game_recommendation(
        total_bankroll=total_bankroll,
        risk_tolerance=selections.get('risk_tolerance', 'moderate'),
        skill_level=selections.get('skill_level', 'intermediate'),
        game_environment=selections.get('game_environment', 'online'),
        cash_stakes_list=stakes_list
    )
    
    # Calculate buy-in multiple for table display
    buy_in_multiple = rec_service.calculate_buy_in_multiple(
        risk_tolerance=selections.get('risk_tolerance', 'moderate'),
        skill_level=selections.get('skill_level', 'intermediate'),
        game_environment=selections.get('game_environment', 'online'),
        game_type='cash'
    )
    
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
        'tools/poker_stakes.html',
        total_bankroll=total_bankroll,
        cash_stakes_table=cash_stakes_table,
        **recommendations,
        bankroll_recommendation=f"{int(buy_in_multiple)} buy-ins recommended",
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
    
    # Load tournament buy-in data from JSON
    json_path = os.path.join(current_app.root_path, 'data', 'tournament_buy_ins.json')
    with open(json_path, 'r') as f:
        tournament_buy_ins = json.load(f)

    # Initialize services
    bankroll_service = BankrollService()
    rec_service = RecommendationService()
    
    bankroll_data = bankroll_service.get_bankroll_breakdown(current_user.id)
    total_bankroll = bankroll_data['total_bankroll']
    
    # Calculate buy-in multiple
    mean_buy_ins = rec_service.calculate_buy_in_multiple(
        risk_tolerance=selections.get('risk_tolerance', 'moderate'),
        skill_level=selections.get('skill_level', 'intermediate'),
        game_environment=selections.get('game_environment', 'online'),
        game_type=selections.get('game_type', 'mtt')
    )

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
            # Pass 1: Populate 'buy_in_dec' and build a map for the recommendation service.
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
            
            # Calculate the recommendation for this specific site using service
            site_recommendations = rec_service.get_tournament_recommendation(
                total_bankroll=total_bankroll,
                risk_tolerance=selections.get('risk_tolerance', 'moderate'),
                skill_level=selections.get('skill_level', 'intermediate'),
                game_type=selections.get('game_type', 'mtt'),
                tournament_stakes_map=site_buyins_map
            )
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

    # Calculate global recommendations using the service
    global_recommendations = rec_service.get_tournament_recommendation(
        total_bankroll=total_bankroll,
        risk_tolerance=selections.get('risk_tolerance', 'moderate'),
        skill_level=selections.get('skill_level', 'intermediate'),
        game_type=selections.get('game_type', 'mtt'),
        tournament_stakes_map=global_buyins_map
    )

    return render_template('tools/tournament_stakes.html',
                           total_bankroll=total_bankroll,
                           game_type=request.args.get('game_type', 'nlhe'),
                           skill_level=request.args.get('skill_level', 'tough'),
                           risk_tolerance=request.args.get('risk_tolerance', 'conservative'),
                           game_environment=request.args.get('game_environment', 'online'),
                           tournament_bankroll_recommendation=f"{int(mean_buy_ins)} buy-ins recommended",
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
    spr_data = None

    try:
        spr_data = get_spr_decision_data()
    except FileNotFoundError:
        flash("SPR decision data file (spr_decisions.json) not found.", "danger")
        logging.error("spr_decisions.json not found in the data directory.")
    except Exception as e:
        flash(f"Error loading or parsing SPR decision data: {e}", "danger")
        logging.error(f"Error parsing spr_decisions.json: {e}", exc_info=True)

    if form.validate_on_submit():
        effective_stack = form.effective_stack.data
        pot_size = form.pot_size.data
        try:
            spr = effective_stack / pot_size

            if spr_data:
                # --- Determine relevant summary decision ---
                # Find the last summary row where the calculated SPR is greater than or equal to the row's SPR
                summary_row = next((row for row in reversed(spr_data['summary']) if spr >= row['spr']), spr_data['summary'][0])
                spr_decision_category = summary_row['category']
                spr_decision_territory = summary_row['territory']

                # --- Determine relevant detailed decision column ---
                detailed_headers = spr_data['detailed']['headers']
                spr_header_index = 0 # Default to first column
                if spr > 13:
                    spr_header_index = 4
                elif spr > 4:
                    spr_header_index = 3
                elif spr > 1:
                    spr_header_index = 2
                else:
                    spr_header_index = 1
                
                if 0 < spr_header_index < len(detailed_headers):
                    spr_detailed_category_header = detailed_headers[spr_header_index]
                    spr_detailed_decisions = []
                    for row_data in spr_data['detailed']['rows']:
                        spr_detailed_decisions.append({
                            'hand_type': row_data[0]['content'],
                            'decision': row_data[spr_header_index]['content'],
                            'decision_class': row_data[spr_header_index]['class']
                        })

        except InvalidOperation:
            flash("Invalid input for stack or pot size.", "danger")
        except ZeroDivisionError:
            flash("Pot size cannot be zero.", "danger")


    return render_template(
        'tools/spr_calculator.html',
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
    service = BankrollService()
    bankroll_data = service.get_bankroll_breakdown(current_user.id)
    current_bankroll = bankroll_data['total_bankroll']
    result = None
    chart_data = None

    if form.validate_on_submit():
        calculation_mode = form.calculation_mode.data
        target_bankroll = form.target_bankroll.data

        amount_needed = target_bankroll - current_bankroll

        if amount_needed <= 0:
            result = f"Congratulations! Your current bankroll of ${current_bankroll:,.2f} already meets or exceeds your target of ${target_bankroll:,.2f}."
        else:
            labels = []
            data_points = []

            if calculation_mode == 'time':
                monthly_profit = form.monthly_profit.data
                if monthly_profit <= 0:
                    result = "With a monthly profit of zero or less, you cannot reach your target bankroll. Please enter a positive value."
                else:
                    months_needed = math.ceil(amount_needed / monthly_profit)
                    
                    # Generate chart data
                    for i in range(int(months_needed) + 1):
                        labels.append(f"Month {i}")
                        projected_val = min(current_bankroll + (monthly_profit * i), target_bankroll)
                        data_points.append(float(projected_val))
                    chart_data = {'labels': labels, 'data': data_points}

                    years = months_needed // 12
                    months = months_needed % 12

                    time_str = ""
                    if years > 0:
                        time_str += f"{years} year{'s' if years > 1 else ''}"
                    if months > 0:
                        if years > 0:
                            time_str += " and "
                        time_str += f"{months} month{'s' if months > 1 else ''}"
                    
                    if not time_str:
                        time_str = "less than a month"

                    result = (f"To reach your target bankroll of ${target_bankroll:,.2f}, you need to accumulate an additional ${amount_needed:,.2f}. "
                              f"At a rate of ${monthly_profit:,.2f} per month, it will take you approximately {time_str}.")
            
            elif calculation_mode == 'profit':
                timeframe_months = form.timeframe_months.data
                if timeframe_months <= 0:
                    result = "Timeframe must be a positive number of months."
                else:
                    required_profit = amount_needed / Decimal(timeframe_months)

                    # Generate chart data
                    for i in range(int(timeframe_months) + 1):
                        labels.append(f"Month {i}")
                        projected_val = min(current_bankroll + (Decimal(required_profit) * i), target_bankroll)
                        data_points.append(float(projected_val))
                    chart_data = {'labels': labels, 'data': data_points}

                    result = (f"To grow your bankroll from ${current_bankroll:,.2f} to ${target_bankroll:,.2f} in {timeframe_months} months, "
                              f"you will need to achieve an average monthly profit of ${required_profit:,.2f}.")

    return render_template('tools/bankroll_goals.html',
                           form=form,
                           current_bankroll=current_bankroll,
                           result=result,
                           chart_data=chart_data)

@tools_bp.route('/tools/plo-hand-strength-evaluator', methods=['GET', 'POST'])
@login_required
def plo_hand_strength_evaluator_page():
    """Renders the PLO Hand Strength Evaluator page and handles evaluation."""
    form = HandStrengthForm()
    evaluation_result = None

    if form.validate_on_submit():
        hand_string = form.hand.data
        position = form.position.data

        # Import necessary functions locally to avoid circular dependency at module level
        from ..routes.hand_eval import evaluate_hand_strength, get_preflop_suggestion, _pretty_print_hand

        tier, reason, score_breakdown, score = evaluate_hand_strength(hand_string)
        action, action_reason = get_preflop_suggestion(tier, position)

        evaluation_result = {
            'hand_string': hand_string,
            'pretty_hand': _pretty_print_hand(hand_string),
            'tier': tier,
            'reason': reason,
            'score_breakdown': score_breakdown,
            'score': f"{score:.1f}",
            'action': action,
            'action_reason': action_reason
        }

    return render_template('tools/plo_hand_strength_evaluator.html', form=form, result=evaluation_result)

@tools_bp.route('/tools/plo-hand-range')
@login_required
def plo_hand_range_page():
    """Renders the PLO Hand Range Visualizer page."""
    return render_template('tools/plo_hand_range.html')