"""PLO hand evaluation and spr quiz."""

from flask import Blueprint, render_template, request, session
from . import algo

hand_eval_bp = Blueprint('hand_eval', __name__)

@hand_eval_bp.route('/tables')
def tables():
    """Tables page route"""
    return render_template('tables.html', title='Tables')

@hand_eval_bp.route('/form')
def form():
    """Form page route"""
    return render_template('form.html', title='Form')

@hand_eval_bp.route('/hand_details', methods=['POST', 'GET'])
def submit_form():
    """Handles form submission and processes data."""
    if request.method == 'POST':
        form_data = algo.process_hand_data(request.form)
        session['form_data'] = form_data

    else: # GET request
        form_data = session.get('form_data', {})
        
    return render_template('hand_details.html', form_data=form_data)

@hand_eval_bp.route('/hand_evaluation', methods=['GET'])
def hand_evaluation():
    form_data = session.get('form_data', {})
    # The template now accesses all data through the form_data dictionary
    return render_template('hand_evaluation.html', form_data=form_data)

@hand_eval_bp.route('/decisions')
def decisions():
    """Decisions page route"""
    return render_template('decisions.html', title='Decisions')

@hand_eval_bp.route('/spr_strategy')
def spr_strategy():
    """SPR Strategy page route"""
    return render_template('spr_strategy.html', title='SPR Strategy')
