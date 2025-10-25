from flask import Blueprint, render_template, redirect, url_for
from flask_security import current_user
from ..utils import get_user_bankroll_data
from ..models import Goal

home_bp = Blueprint("home", __name__)

@home_bp.route("/")
def home():
    """Main page."""
    if not current_user.is_authenticated:
        return redirect(url_for('about.about'))

    bankroll_data = get_user_bankroll_data(current_user.id)

    # Fetch the active goal and calculate progress
    active_goal = Goal.query.filter_by(user_id=current_user.id, status='active').first()
    goal_progress = None
    if active_goal:
        if active_goal.goal_type == 'profit_target':
            current_value = bankroll_data.get('total_profit', 0.0)
        else: # Default to bankroll_target
            current_value = bankroll_data.get('total_bankroll', 0.0)

        if active_goal.target_value > 0:
            goal_progress = (current_value / active_goal.target_value) * 100
        else:
            goal_progress = 0

    return render_template("index.html",
                           current_poker_total=bankroll_data['current_poker_total'],
                           previous_poker_total=bankroll_data['previous_poker_total'],
                           current_asset_total=bankroll_data['current_asset_total'],
                           previous_asset_total=bankroll_data['previous_asset_total'],
                           total_withdrawals=bankroll_data['total_withdrawals'],
                           total_deposits=bankroll_data['total_deposits'],
                           total_bankroll=bankroll_data['total_bankroll'],
                           total_profit=bankroll_data['total_profit'],
                           active_goal=active_goal,
                           goal_progress=goal_progress)

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email

class DummyLoginForm(FlaskForm):
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

@home_bp.route("/debug_login")
def debug_login():
    dummy_form = DummyLoginForm()
    return render_template("security/login_user.html", form=dummy_form)