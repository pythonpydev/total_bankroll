from flask import Blueprint, render_template, redirect, request, url_for, current_app, flash
from flask_security import login_required, current_user
from datetime import datetime, UTC
from decimal import Decimal
from sqlalchemy import func
from ..services import BankrollService
from ..utils import get_sorted_currencies
from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SelectField, SubmitField, DateField
from wtforms.validators import DataRequired, NumberRange
from ..models import db, Deposits, Currency

deposit_bp = Blueprint("deposit", __name__)

class UpdateDepositForm(FlaskForm):
    date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()])
    amount = DecimalField('Amount', validators=[DataRequired(), NumberRange(min=0.01)])
    currency = SelectField('Currency', coerce=str, validators=[DataRequired()])
    submit = SubmitField('Update Deposit')

@deposit_bp.route("/deposit")
@login_required
def deposit():
    """Deposit page."""
    from ..models import Deposits, Currency
    currency_symbols = {row.code: row.symbol for row in db.session.query(Currency.code, Currency.symbol).all()}

    # Use BankrollService to get bankroll data
    service = BankrollService()
    bankroll_data = service.get_bankroll_breakdown(current_user.id)
    total_net_worth = bankroll_data['total_bankroll']

    # Get date range from request arguments
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')

    # Get deposits with currency conversion to USD
    deposits_query = db.session.query(
        Deposits.id,
        Deposits.date,
        Deposits.amount.label('original_amount'),
        Deposits.last_updated,
        Deposits.currency,
        Currency.rate.label('exchange_rate'),
        Currency.name.label('currency_name')
    ).join(Currency, Deposits.currency == Currency.code)\
     .filter(Deposits.user_id == current_user.id)

    # Apply date filters if they exist
    if start_date_str:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        deposits_query = deposits_query.filter(Deposits.date >= start_date)
    if end_date_str:
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        deposits_query = deposits_query.filter(Deposits.date <= end_date)

    deposits_raw = deposits_query.order_by(Deposits.date.desc()).all()
    current_app.logger.debug(f"deposits_raw: {deposits_raw}")

    # Process deposits to add USD calculations and currency symbols
    deposit_data = []
    for deposit in deposits_raw:
        deposit_dict = {
            'id': deposit.id,
            'date': deposit.date.strftime("%Y-%m-%d"),
            'original_amount': deposit.original_amount,
            'last_updated': deposit.last_updated,
            'currency': deposit.currency_name if deposit.currency_name else "N/A",
            'amount_usd': (deposit.original_amount / deposit.exchange_rate) if deposit.exchange_rate else Decimal(0),
            'currency_symbol': currency_symbols.get(deposit.currency, deposit.currency),
            'currency_name': deposit.currency_name
        }
        deposit_data.append(deposit_dict)

    today = datetime.now().strftime("%Y-%m-%d")
    currencies = get_sorted_currencies()
    default_currency = current_user.default_currency_code if hasattr(current_user, 'default_currency_code') else 'USD'

    return render_template("info/deposit.html", 
                           deposits=deposit_data, 
                           today=today, 
                           total_net_worth=total_net_worth, 
                           currencies=currencies,
                           default_currency=default_currency,
                           start_date=start_date_str,
                           end_date=end_date_str)

@deposit_bp.route("/update_deposit/<int:deposit_id>", methods=["GET", "POST"])
@login_required
def update_deposit(deposit_id):
    """Update a deposit transaction."""
    from ..models import Deposits, Currency
    deposit_item = db.session.get(Deposits, deposit_id)
    if not deposit_item:
        flash("Deposit not found.", "danger")
        return redirect(url_for("deposit.deposit"))
    if deposit_item.user_id != current_user.id:
        flash("Not authorized to update this deposit.", "danger")
        return redirect(url_for("deposit.deposit"))

    form = UpdateDepositForm(obj=deposit_item)
    currencies = get_sorted_currencies()
    form.currency.choices = [(c['code'], c['name']) for c in currencies]

    if form.validate_on_submit():
        try:
            deposit_item.date = form.date.data
            deposit_item.amount = form.amount.data
            deposit_item.currency = form.currency.data
            deposit_item.last_updated = datetime.now(UTC)
            db.session.commit()
            flash("Deposit updated successfully!", "success")
        except (ValueError, Exception) as e:
            db.session.rollback()
            flash(f"An error occurred: {e}", "danger")
        return redirect(url_for("deposit.deposit"))

    # For GET request, pre-populate the form
    if request.method == 'GET':
        form.currency.data = deposit_item.currency

    return render_template("partials/_modal_form.html", form=form, title="Edit Deposit", action_url=url_for('deposit.update_deposit', deposit_id=deposit_id))

@deposit_bp.route("/delete_deposit/<int:deposit_id>", methods=["POST"])
@login_required
def delete_deposit(deposit_id):
    """Delete a deposit transaction."""
    from ..models import Deposits
    deposit_item = db.session.query(Deposits).filter_by(id=deposit_id, user_id=current_user.id).first()
    if deposit_item:
        db.session.delete(deposit_item)
        db.session.commit()
        flash("Deposit deleted successfully!", "success")
    else:
        flash("Deposit not found.", "danger")
    return redirect(url_for("deposit.deposit"))