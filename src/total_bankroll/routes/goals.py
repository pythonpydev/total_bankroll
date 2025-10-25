from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_security import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SubmitField, SelectField
from wtforms.fields import DateField
from wtforms.validators import DataRequired, NumberRange, ValidationError
from datetime import datetime, date, UTC

from ..extensions import db
from ..models import Goal
from ..utils import get_user_bankroll_data

goals_bp = Blueprint('goals', __name__, url_prefix='/goals')

def validate_end_date(form, field):
    if field.data and field.data < date.today():
        raise ValidationError("End date cannot be in the past.")

class GoalForm(FlaskForm):
    """Form for adding or editing a goal."""
    goal_type = SelectField('Goal Type', choices=[('bankroll_target', 'Bankroll Target'), ('profit_target', 'Profit Target')], validators=[DataRequired()])
    name = StringField('Goal Name', validators=[DataRequired()])
    target_value = DecimalField('Target Value ($)', validators=[DataRequired(), NumberRange(min=0.01)])
    end_date = DateField('Target Date', validators=[DataRequired(), validate_end_date], format='%Y-%m-%d')
    submit = SubmitField('Set Goal')

@goals_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    """Page to view and create goals."""
    form = GoalForm()
    bankroll_data = get_user_bankroll_data(current_user.id)
    current_bankroll = bankroll_data.get('total_bankroll', 0.0)
    current_profit = bankroll_data.get('total_profit', 0.0)

    if form.validate_on_submit():
        # Check for any existing active goal
        existing_goal = Goal.query.filter_by(user_id=current_user.id, status='active').first()
        if existing_goal:
            flash('You already have an active goal. Please complete or archive it before creating a new one.', 'warning')
            return redirect(url_for('goals.index'))

        # Convert date to datetime
        end_datetime = datetime.combine(form.end_date.data, datetime.min.time()).replace(tzinfo=UTC)

        new_goal = Goal(
            user_id=current_user.id,
            name=form.name.data,
            goal_type=form.goal_type.data,
            target_value=form.target_value.data,
            end_date=end_datetime,
            status='active'
        )
        db.session.add(new_goal)
        db.session.commit()
        flash('New bankroll goal has been set!', 'success')
        return redirect(url_for('goals.index'))

    # Fetch goals for display
    active_goals = Goal.query.filter_by(user_id=current_user.id, status='active').order_by(Goal.end_date.asc()).all()
    completed_goals = Goal.query.filter_by(user_id=current_user.id, status='completed').order_by(Goal.completed_at.desc()).all()
    archived_goals = Goal.query.filter_by(user_id=current_user.id, status='archived').order_by(Goal.end_date.desc()).all()

    # Calculate progress for active goals
    for goal in active_goals:
        current_value = 0
        if goal.goal_type == 'profit_target':
            current_value = current_profit
        else:  # Default to bankroll_target
            current_value = current_bankroll
        
        goal.progress = (current_value / goal.target_value) * 100 if goal.target_value > 0 else 0
        goal.current_value = current_value

        if goal.progress >= 100 and goal.status == 'active':
            goal.status = 'completed'
            goal.completed_at = datetime.now(UTC)
            flash(f'Congratulations! You automatically completed the goal: "{goal.name}".', 'success')
            db.session.commit()
            return redirect(url_for('goals.index'))

    return render_template('goals.html',
                           form=form,
                           active_goals=active_goals,
                           completed_goals=completed_goals,
                           archived_goals=archived_goals,
                           current_bankroll=current_bankroll,
                           current_profit=current_profit)

@goals_bp.route('/<int:goal_id>/archive', methods=['POST'])
@login_required
def archive_goal(goal_id):
    """Archive an active goal."""
    goal = Goal.query.filter_by(id=goal_id, user_id=current_user.id).first_or_404()
    if goal.status in ['active', 'completed']:
        goal.status = 'archived'
        db.session.commit()
        flash(f'Goal "{goal.name}" has been archived.', 'success')
    else:
        flash('This goal cannot be archived.', 'warning')
    return redirect(url_for('goals.index'))

@goals_bp.route('/<int:goal_id>/complete', methods=['POST'])
@login_required
def complete_goal(goal_id):
    """Mark an active goal as completed."""
    goal = Goal.query.filter_by(id=goal_id, user_id=current_user.id).first_or_404()
    if goal.status == 'active':
        goal.status = 'completed'
        goal.completed_at = datetime.now(UTC)
        db.session.commit()
        flash(f'Congratulations! You completed the goal: "{goal.name}".', 'success')
    else:
        flash('Only active goals can be marked as complete.', 'warning')
    return redirect(url_for('goals.index'))