from flask import Blueprint, render_template, redirect, request, url_for, current_app
from flask_security import login_required, current_user
from datetime import datetime
from decimal import Decimal
from sqlalchemy import func
from ..extensions import db
from ..models import Deposits, Currency, SiteHistory, Sites, AssetHistory, Assets, Drawings

deposit_bp = Blueprint("deposit", __name__)

@deposit_bp.route("/deposit")
@login_required
def deposit():
    """Deposit page."""
    # Get currency symbols
    currency_symbols = {row.code: row.symbol for row in db.session.query(Currency.code, Currency.symbol).all()}

    # Get current poker site totals from site_history
    current_poker_total = db.session.query(func.sum(SiteHistory.amount / Currency.rate)).\
        join(Sites, SiteHistory.site_id == Sites.id).\
        join(Currency, SiteHistory.currency == Currency.code).\
        filter(SiteHistory.user_id == current_user.id).\
        filter(SiteHistory.recorded_at == db.session.query(func.max(SiteHistory.recorded_at))
               .filter_by(site_id=SiteHistory.site_id, user_id=current_user.id).correlate(SiteHistory).scalar_subquery()).\
        scalar() or Decimal(0)

    # Get current asset totals from asset_history
    current_asset_total = db.session.query(func.sum(AssetHistory.amount / Currency.rate)).\
        join(Assets, AssetHistory.asset_id == Assets.id).\
        join(Currency, AssetHistory.currency == Currency.code).\
        filter(AssetHistory.user_id == current_user.id).\
        filter(AssetHistory.recorded_at == db.session.query(func.max(AssetHistory.recorded_at))
               .filter_by(asset_id=AssetHistory.asset_id, user_id=current_user.id).correlate(AssetHistory).scalar_subquery()).\
        scalar() or Decimal(0)

    # Get current total of all withdrawals
    total_withdrawals = db.session.query(func.sum(Drawings.amount / Currency.rate)).\
        join(Currency, Drawings.currency == Currency.code).\
        filter(Drawings.user_id == current_user.id).\
        scalar() or Decimal(0)

    total_net_worth = current_poker_total + current_asset_total - total_withdrawals

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
            'currency': deposit.currency,
            'amount_usd': (deposit.original_amount / deposit.exchange_rate) if deposit.exchange_rate else Decimal(0),
            'currency_symbol': currency_symbols.get(deposit.currency, deposit.currency),
            'currency_name': deposit.currency_name
        }
        deposit_data.append(deposit_dict)

    today = datetime.now().strftime("%Y-%m-%d")
    currencies = db.session.query(Currency.name).\
        order_by(
            db.case(
                (Currency.name == 'US Dollar', 1),
                (Currency.name == 'British Pound', 2),
                (Currency.name == 'Euro', 3),
                else_=4
            ),
            Currency.name
        ).all()
    currencies = [c.name for c in currencies]

    return render_template("deposit.html", deposits=deposit_data, today=today, total_net_worth=total_net_worth, currencies=currencies)