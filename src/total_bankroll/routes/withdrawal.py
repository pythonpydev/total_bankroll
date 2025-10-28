from flask import Blueprint, render_template, redirect, request, url_for, current_app, flash
from flask_security import login_required, current_user
from datetime import datetime, UTC
from decimal import Decimal
from sqlalchemy import func
from ..utils import get_user_bankroll_data, get_sorted_currencies
from ..models import db
from ..models import Drawings, Currency, User
from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SelectField, SubmitField, DateField
from wtforms.validators import DataRequired, NumberRange

withdrawal_bp = Blueprint("withdrawal", __name__)

class UpdateWithdrawalForm(FlaskForm):
    date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()])
    amount = DecimalField('Amount', validators=[DataRequired(), NumberRange(min=0.01)])
    currency = SelectField('Currency', coerce=str, validators=[DataRequired()])
    submit = SubmitField('Update Withdrawal')

@withdrawal_bp.route("/withdrawal")
@login_required
def withdrawal():
    """Withdrawal page."""
    # Get currency symbols
    currency_symbols = {row.code: row.symbol for row in db.session.query(Currency.code, Currency.symbol).all()}
    current_app.logger.debug(f"currency_symbols dictionary: {currency_symbols}")

    # Use the centralized utility function to get bankroll data
    bankroll_data = get_user_bankroll_data(current_user.id)
    total_net_worth = bankroll_data['total_bankroll']

    # Get date range from request arguments
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')

    # Get withdrawals with currency conversion to USD
    withdrawals_query = db.session.query(
        Drawings.id,
        Drawings.date,
        Drawings.amount.label('original_amount'),
        Drawings.last_updated,
        Drawings.currency,
        Currency.rate.label('exchange_rate'),
        Currency.name.label('currency_name')
    ).\
        join(Currency, Drawings.currency == Currency.code).\
        filter(Drawings.user_id == current_user.id).\
        order_by(Drawings.date.desc())

    # Apply date filters if they exist
    if start_date_str:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        withdrawals_query = withdrawals_query.filter(Drawings.date >= start_date)
    if end_date_str:
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        withdrawals_query = withdrawals_query.filter(Drawings.date <= end_date)

    withdrawals_raw = withdrawals_query.all()
    current_app.logger.debug(f"withdrawals_raw: {withdrawals_raw}")

    # Process withdrawals to add USD calculations and currency symbols
    withdrawal_data = []
    for withdrawal_item in withdrawals_raw:
        withdrawal_dict = {
            'id': withdrawal_item.id,
            'date': withdrawal_item.date.strftime("%Y-%m-%d"),
            'original_amount': withdrawal_item.original_amount,
            'last_updated': withdrawal_item.last_updated,
            'currency': withdrawal_item.currency_name if withdrawal_item.currency_name else "N/A",
            'amount_usd': (withdrawal_item.original_amount / withdrawal_item.exchange_rate) if withdrawal_item.exchange_rate else Decimal(0),
            'currency_symbol': currency_symbols.get(withdrawal_item.currency, withdrawal_item.currency)
        }
        withdrawal_data.append(withdrawal_dict)

    today = datetime.now().strftime("%Y-%m-%d")
    currencies = get_sorted_currencies()

    current_app.logger.debug(f"withdrawal_data: {withdrawal_data}")
    return render_template("withdrawal.html", 
                           drawings=withdrawal_data, 
                           today=today, 
                           total_net_worth=total_net_worth, 
                           currencies=currencies,
                           start_date=start_date_str,
                           end_date=end_date_str)

@withdrawal_bp.route("/update_withdrawal/<int:withdrawal_id>", methods=["GET", "POST"])
@login_required
def update_withdrawal(withdrawal_id):
    """Update a withdrawal transaction."""
    withdrawal_item = db.session.get(Drawings, withdrawal_id)
    if not withdrawal_item:
        flash("Withdrawal not found.", "danger")
        return redirect(url_for("withdrawal.withdrawal"))
    if withdrawal_item.user_id != current_user.id:
        flash("Not authorized to update this withdrawal.", "danger")
        return redirect(url_for("withdrawal.withdrawal"))

    form = UpdateWithdrawalForm(obj=withdrawal_item)
    currencies = get_sorted_currencies()
    form.currency.choices = [(c['code'], c['name']) for c in currencies]

    if form.validate_on_submit():
        try:
            withdrawal_item.date = form.date.data
            withdrawal_item.amount = form.amount.data
            withdrawal_item.currency = form.currency.data
            withdrawal_item.last_updated = datetime.now(UTC)
            db.session.commit()
            flash("Withdrawal updated successfully!", "success")
        except (ValueError, Exception) as e:
            db.session.rollback()
            flash(f"An error occurred: {e}", "danger")
        return redirect(url_for("withdrawal.withdrawal"))

    # For GET request, pre-populate the form
    if request.method == 'GET':
        form.currency.data = withdrawal_item.currency

    return render_template("partials/_modal_form.html", form=form, title="Edit Withdrawal")