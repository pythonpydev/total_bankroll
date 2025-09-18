"""PLO hand evaluation and spr quiz."""

from flask import Blueprint, render_template, request, session, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, SubmitField
from wtforms.validators import DataRequired, Optional
from . import algo

hand_eval_bp = Blueprint('hand_eval', __name__)

class ButtonPositionForm(FlaskForm):
    button_position = IntegerField('Button Position')
    submit = SubmitField('Submit')

class HandForm(FlaskForm):
    small_blind = IntegerField('Small Blind', validators=[DataRequired()])
    big_blind = IntegerField('Big Blind', validators=[DataRequired()])
    hero_stack = IntegerField("Hero's Chip Stack", validators=[DataRequired()])
    hero_position = StringField("Hero's Position", validators=[DataRequired()])
    hero_hand = StringField("Hero's Hand", validators=[DataRequired()])
    board = StringField('Board Cards', validators=[DataRequired()])
    opponent_stack = IntegerField("Opponent's Chip Stack", validators=[DataRequired()])
    opponent_position = StringField("Opponent's Position", validators=[DataRequired()])
    opponent_hand = StringField("Opponent's Hand", validators=[DataRequired()])
    pot_size = IntegerField('Pot Size', validators=[DataRequired()])
    bet_size = IntegerField('Bet Size', validators=[Optional()])

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
    hand_form = HandForm()
    if request.method == 'POST' and hand_form.validate_on_submit():
        form_data = algo.process_hand_data(request.form)
        session['form_data'] = form_data
    else:  # GET request
        form_data = session.get('form_data', {})
    return render_template('hand_details.html', form_data=form_data)

@hand_eval_bp.route('/hand_evaluation', methods=['GET'])
def hand_evaluation():
    form_data = session.get('form_data', {})
    return render_template('hand_evaluation.html', form_data=form_data)

@hand_eval_bp.route('/decisions')
def decisions():
    """Decisions page route"""
    return render_template('decisions.html', title='Decisions')

@hand_eval_bp.route('/spr_strategy')
def spr_strategy():
    """SPR Strategy page route"""
    return render_template('spr_strategy.html', title='SPR Strategy')