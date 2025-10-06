"""PLO hand evaluation and spr quiz."""

import re
import logging
import json
import os
import random
from flask import Blueprint, render_template, request, session, redirect, url_for, flash, current_app
from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, SubmitField, SelectField, RadioField
from wtforms.validators import DataRequired, Optional, ValidationError
from . import algo

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

@hand_eval_bp.route('/tables')
def tables():
    """Tables page route"""
    return render_template('tables.html', title='Tables')

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
        form_data = algo.process_hand_data(request.form, button_position)
        session['form_data'] = form_data
        return render_template('hand_details.html', form_data=form_data)

    # If validation fails on POST, or it's a GET without session data, show the form.
    if request.method == 'POST': # Only flash errors on a failed POST
        logging.debug(f"Form validation failed. Errors: {hand_form.errors}")
        for field, errors in hand_form.errors.items():
            for error in errors:
                flash(f"Error in {getattr(hand_form, field).label.text}: {error}", 'error')

    return render_template('plo_hand_form.html', title='PLO Hand Form', button_position=button_position, button_form=button_form, hand_form=hand_form)

@hand_eval_bp.route('/hand_evaluation', methods=['GET'])
def hand_evaluation():
    form_data = session.get('form_data', {})
    if not form_data:
        flash('No hand data found. Please submit a hand first.', 'warning')
        return redirect(url_for('hand_eval.plo_hand_form'))

    return render_template('hand_evaluation.html', form_data=form_data, title="Hand Evaluation")

@hand_eval_bp.route('/decisions')
def decisions():
    """Decisions page route"""
    return render_template('decisions.html', title='Decisions')

@hand_eval_bp.route('/spr_strategy')
def spr_strategy():
    """SPR Strategy page route"""
    return render_template('spr_strategy.html', title='SPR Strategy')

@hand_eval_bp.route('/pot-odds-equity')
def pot_odds_equity():
    """Pot Odds vs Equity explanation page route"""
    return render_template('pot_odds_equity.html', title='Pot Odds vs Equity')

@hand_eval_bp.route('/hud-player-types')
def hud_player_types():
    """HUD Player Types reference page route"""
    try:
        # Use open_resource for a more robust path to the data file
        with current_app.open_resource('data/hud_player_types.json', 'r') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        flash(f"Could not load HUD player type data: {e}", "error")
        data = {'player_types': [], 'stats': []} # Provide empty data on error
    return render_template('hud_player_type.html', title='HUD Player Types', data=data)

@hand_eval_bp.route('/player-types-article')
def player_types_article():
    """Player Types article page route"""
    return render_template('player_types_article.html', title='Player Types Article')

@hand_eval_bp.route('/player-color-scheme')
def player_color_scheme():
    """Player color scheme article page route"""
    return render_template('player_color_scheme.html', title='Player Color Scheme')

@hand_eval_bp.route('/card_selector')
def card_selector():
    """Card selector page route"""
    return render_template('card_selector.html', title='Card Selector')

def _parse_plo_article(markdown_text):
    """
    Parses a subset of Markdown with special handling for PLO hand notations into HTML.
    - Handles ### and #### for h3/h4 tags.
    - Handles paragraphs.
    - Handles Markdown tables.
    - Converts card notations like A♠K♥ into images.
    """
    html = []
    in_table = False
    lines = markdown_text.strip().split('\n')

    def render_hand(text):
        """Converts card notations in a string to HTML images."""
        suit_map = {'♠': 'S', '♥': 'H', '♦': 'D', '♣': 'C'}
        
        processed_text = ""
        i = 0
        while i < len(text):
            char = text[i]
            next_char = text[i+1] if i + 1 < len(text) else ''
            
            if next_char in suit_map:
                rank = char
                suit_symbol = next_char
                suit_char = suit_map.get(suit_symbol, '')
                
                if rank == 'T':
                    rank_char = '10'
                else:
                    rank_char = rank
                
                image_name = f"{rank_char.upper()}{suit_char.upper()}.png"
                processed_text += f'<img src="/static/images/cards/{image_name}" alt="{rank}{suit_symbol}" class="card-image-small" style="height: 1.5em; margin: 0 1px;">'
                i += 2
            else:
                processed_text += char
                i += 1
        return processed_text

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if line.startswith('#### '):
            if in_table:
                html.append('</tbody></table>')
                in_table = False
            html.append(f'<h4>{render_hand(line[5:])}</h4>')
        elif line.startswith('### '):
            if in_table:
                html.append('</tbody></table>')
                in_table = False
            html.append(f'<h3>{render_hand(line[4:])}</h3>')
        elif line.startswith('|'):
            cells = [cell.strip() for cell in line.split('|')][1:-1]
            if not in_table:
                html.append('<table class="table table-bordered"><thead><tr>')
                for cell in cells:
                    html.append(f'<th>{render_hand(cell)}</th>')
                html.append('</tr></thead><tbody>')
                in_table = True
            elif '---' in cells[0]:
                continue
            else:
                html.append('<tr>')
                for i, cell in enumerate(cells):
                    if i == 0:
                        html.append(f'<td><strong>{render_hand(cell)}</strong></td>')
                    else:
                        html.append(f'<td>{render_hand(cell)}</td>')
                html.append('</tr>')
        else:
            if in_table:
                html.append('</tbody></table>')
                in_table = False
            html.append(f'<p>{render_hand(line)}</p>')

    if in_table:
        html.append('</tbody></table>')

    return '\n'.join(html)

@hand_eval_bp.route('/plo-starting-hand-strength')
def plo_starting_hand_strength():
    """PLO Starting Hand Strength article page route"""
    article_path = '' # Initialize path for error message
    try:
        # Construct an absolute path to the article
        project_root = '/home/ed/MEGA/total_bankroll/'
        article_path = os.path.join(project_root, 'resources', 'articles', 'markdown', 'Absolute Starting Hand Strength in Pot Limit Omaha (PLO) for 6-Max Tables.md')
        with open(article_path, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        html_content = _parse_plo_article(markdown_content)
    except FileNotFoundError:
        flash("Article not found. Please check the file path.", "error")
        html_content = f"<p>Article content could not be loaded. Path does not exist: {article_path}</p>"
    except Exception as e:
        flash(f"An error occurred: {e}", "error")
        html_content = "<p>An error occurred while processing the article.</p>"
    return render_template('plo_starting_hand_strength.html', title='PLO Starting Hand Strength', content=html_content)

class HudStatsQuizForm(FlaskForm):
    """Form for starting the HUD stats quiz."""
    num_questions = SelectField(
        'Number of Questions',
        choices=[('5', '5'), ('10', '10'), ('20', '20')],
        validators=[DataRequired()]
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
    form.answer.choices = [(ans, ans) for ans in question['answers']]

    if form.validate_on_submit():
        user_answer = form.answer.data
        if question['correct_answer'] == user_answer:
            session['score'] = session.get('score', 0) + 1
        else:
            incorrect = {
                'question': question['question'],
                'your_answer': user_answer,
                'correct_answer': question['correct_answer']
            }
            session['incorrect_answers'].append(incorrect)
        session['current_question'] = current_question_index + 1
        return redirect(url_for('hand_eval.quiz'))

    return render_template(
        'quiz.html',
        title='HUD Stats Quiz',
        question=question,
        form=form,
        question_number=current_question_index + 1,
        total_questions=len(questions)
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

    incorrect_answers = session.get('incorrect_answers', [])
    return render_template(
        'quiz_results.html',
        title='Quiz Results',
        score=score,
        total_questions=total_questions,
        percentage=percentage,
        rating=user_rating,
        incorrect_answers=incorrect_answers
    )