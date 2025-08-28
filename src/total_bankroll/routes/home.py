from flask import Blueprint, render_template, redirect, url_for
from flask_security import current_user
from ..utils import get_user_bankroll_data

home_bp = Blueprint("home", __name__)

@home_bp.route("/")
def home():
    """Main page."""
    if not current_user.is_authenticated:
        return redirect(url_for('about.about'))

    bankroll_data = get_user_bankroll_data(current_user.id)

    return render_template("index.html",
                           current_poker_total=bankroll_data['current_poker_total'],
                           previous_poker_total=bankroll_data['previous_poker_total'],
                           current_asset_total=bankroll_data['current_asset_total'],
                           previous_asset_total=bankroll_data['previous_asset_total'],
                           total_withdrawals=bankroll_data['total_withdrawals'],
                           total_deposits=bankroll_data['total_deposits'],
                           total_bankroll=bankroll_data['total_bankroll'],
                           total_profit=bankroll_data['total_profit'])

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