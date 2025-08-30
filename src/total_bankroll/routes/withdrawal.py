from flask import Blueprint, render_template, redirect, request, url_for, current_app
from flask_security import login_required, current_user
from datetime import datetime
from decimal import Decimal
from sqlalchemy import func
from ..extensions import db
from ..models import Drawings, Currency, SiteHistory, Sites, AssetHistory, Assets

withdrawal_bp = Blueprint("withdrawal", __name__)

@withdrawal_bp.route("/withdrawal")
@login_required
def withdrawal():
    """Withdrawal page."""
    # Get currency symbols
    currency_symbols = {row.code: row.symbol for row in db.session.query(Currency.code, Currency.symbol).all()}
    current_app.logger.debug(f"currency_symbols dictionary: {currency_symbols}")

    # Get current poker site totals from site_history
    current_poker_total = db.session.query(func.sum(SiteHistory.amount / Currency.rate)).\
        join(Sites, SiteHistory.site_id == Sites.id).\
        join(Currency, SiteHistory.currency == Currency.name).\
        filter(SiteHistory.user_id == current_user.id).\
        filter(SiteHistory.recorded_at == db.session.query(func.max(SiteHistory.recorded_at)).\
               filter_by(site_id=SiteHistory.site_id, user_id=current_user.id).scalar_subquery()).\
        scalar() or Decimal(0)

    # Get current asset totals from asset_history
    current_asset_total = db.session.query(func.sum(AssetHistory.amount / Currency.rate)).\
        join(Assets, AssetHistory.asset_id == Assets.id).\
        join(Currency, AssetHistory.currency == Currency.name).\
        filter(AssetHistory.user_id == current_user.id).\
        filter(AssetHistory.recorded_at == db.session.query(func.max(AssetHistory.recorded_at)).\
               filter_by(asset_id=AssetHistory.asset_id, user_id=current_user.id).scalar_subquery()).\
        scalar() or Decimal(0)

    # Get current total of all withdrawals
    total_withdrawals = db.session.query(func.sum(Drawings.amount / Currency.rate)).\
        join(Currency, Drawings.currency == Currency.name).\
        filter(Drawings.user_id == current_user.id).\
        scalar() or Decimal(0)

    total_net_worth = current_poker_total + current_asset_total - total_withdrawals

    # Get withdrawals with currency conversion to USD
    withdrawals_raw = db.session.query(
        Drawings.id,
        Drawings.date,
        Drawings.amount.label('original_amount'),
        Drawings.last_updated,
        Drawings.currency,
        Currency.rate.label('exchange_rate')
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
            'currency': withdrawal_item.currency if withdrawal_item.currency else "N/A",
            'amount_usd': (withdrawal_item.original_amount / withdrawal_item.exchange_rate) if withdrawal_item.exchange_rate else Decimal(0),
            'currency_symbol': currency_symbols.get(withdrawal_item.currency, withdrawal_item.currency)
        }
        withdrawal_data.append(withdrawal_dict)

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

    current_app.logger.debug(f"withdrawal_data: {withdrawal_data}")
    return render_template("withdrawal.html", drawings=withdrawal_data, today=today, total_net_worth=total_net_worth, currencies=currencies)