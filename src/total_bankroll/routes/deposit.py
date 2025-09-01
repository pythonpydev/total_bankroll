from flask import Blueprint, render_template, redirect, request, url_for, current_app
from flask_security import login_required, current_user
from datetime import datetime
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

    # Get deposits with currency conversion to USD
    deposits_raw = db.session.query(
        Deposits.id,
        Deposits.date,
        Deposits.amount.label('original_amount'),
        Deposits.last_updated,
        Deposits.currency,
        Currency.rate.label('exchange_rate'),
        Currency.name.label('currency_name')
    ).join(Currency, Deposits.currency == Currency.code)\
     .filter(Deposits.user_id == current_user.id)\
     .order_by(Deposits.date.desc()).all()
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
    currencies = [c['name'] for c in get_sorted_currencies()]

    return render_template("deposit.html", deposits=deposit_data, today=today, total_net_worth=total_net_worth, currencies=currencies)