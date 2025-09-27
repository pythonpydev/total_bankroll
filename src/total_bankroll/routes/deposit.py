from flask import Blueprint, render_template, redirect, request, url_for, current_app, flash
from flask_security import login_required, current_user
from datetime import datetime, UTC
from decimal import Decimal
from sqlalchemy import func
from ..utils import get_user_bankroll_data, get_sorted_currencies
from ..extensions import db

deposit_bp = Blueprint("deposit", __name__)

@deposit_bp.route("/deposit")
@login_required
def deposit():
    """Deposit page."""
    from ..models import Deposits, Currency
    currency_symbols = {row.code: row.symbol for row in db.session.query(Currency.code, Currency.symbol).all()}

    # Use the centralized utility function to get bankroll data
    bankroll_data = get_user_bankroll_data(current_user.id)
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

    return render_template("deposit.html", 
                           deposits=deposit_data, 
                           today=today, 
                           total_net_worth=total_net_worth, 
                           currencies=currencies,
                           start_date=start_date_str,
                           end_date=end_date_str)

@deposit_bp.route("/update_deposit/<int:deposit_id>", methods=["GET", "POST"])
@login_required
def update_deposit(deposit_id):
    """Update a deposit transaction."""
    from ..models import Deposits
    deposit_item = db.session.query(Deposits).filter_by(id=deposit_id, user_id=current_user.id).first()
    if not deposit_item:
        flash("Deposit not found.", "danger")
        return redirect(url_for("deposit.deposit"))

    if request.method == "POST":
        date_str = request.form.get("date", "")
        amount_str = request.form.get("amount", "")
        currency_code = request.form.get("currency", "USD")

        if not date_str or not amount_str:
            flash("Date and amount are required", "danger")
            return redirect(url_for("deposit.deposit"))

        try:
            deposit_item.date = datetime.strptime(date_str, "%Y-%m-%d")
            amount = round(Decimal(amount_str), 2)
            if amount <= 0:
                flash("Amount must be positive", "danger")
                return redirect(url_for("deposit.deposit"))
            deposit_item.amount = amount
            deposit_item.currency = currency_code
            deposit_item.last_updated = datetime.now(UTC)
            db.session.commit()
            flash("Deposit updated successfully!", "success")
        except (ValueError, Exception) as e:
            db.session.rollback()
            flash(f"An error occurred: {e}", "danger")
        
        return redirect(url_for("deposit.deposit"))
    else:
        # GET request
        currencies = get_sorted_currencies()
        return render_template("update_deposit.html", deposit=deposit_item, currencies=currencies)

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