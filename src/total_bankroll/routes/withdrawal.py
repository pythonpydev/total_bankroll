from flask import Blueprint, render_template, redirect, request, url_for, current_app
from flask_security import login_required, current_user
from datetime import datetime
from decimal import Decimal
from sqlalchemy import func
from ..utils import get_user_bankroll_data, get_sorted_currencies
from ..extensions import db
from ..models import Drawings, Currency

withdrawal_bp = Blueprint("withdrawal", __name__)

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

    # Get withdrawals with currency conversion to USD
    withdrawals_raw = db.session.query(
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
        order_by(Drawings.date.desc()).all()
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
    currencies = [c['name'] for c in get_sorted_currencies()]

    current_app.logger.debug(f"withdrawal_data: {withdrawal_data}")
    return render_template("withdrawal.html", drawings=withdrawal_data, today=today, total_net_worth=total_net_worth, currencies=currencies)