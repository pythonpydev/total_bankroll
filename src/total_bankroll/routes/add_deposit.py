from flask import Blueprint, render_template, redirect, request, url_for, flash, current_app
from datetime import datetime
from decimal import Decimal
from sqlalchemy import func
from flask_security import login_required, current_user
from ..extensions import db
from ..models import Deposits, Currency, SiteHistory, Sites, AssetHistory, Assets, Drawings

add_deposit_bp = Blueprint("add_deposit", __name__)

@add_deposit_bp.route("/add_deposit", methods=["GET", "POST"])
@login_required
def add_deposit():
    """Add a deposit transaction."""
    if request.method == "POST":
        date_str = request.form.get("date", "")
        amount_str = request.form.get("amount", "")
        currency_name = request.form.get("currency", "US Dollar")

        current_app.logger.debug(f"Form data: date={date_str}, amount={amount_str}, currency={currency_name}")

        if not date_str or not amount_str:
            flash("Date and amount are required", "danger")
            return redirect(url_for("deposit.deposit"))

        try:
            date = datetime.strptime(date_str, "%Y-%m-%d")
            amount = round(Decimal(amount_str), 2)
            if amount <= 0:
                flash("Amount must be positive", "danger")
                return redirect(url_for("deposit.deposit"))
        except ValueError as e:
            current_app.logger.debug(f"ValueError during deposit processing: {e}")
            flash("Invalid date or amount format", "danger")
            return redirect(url_for("deposit.deposit"))

        new_deposit = Deposits(
            date=date,
            amount=amount,
            last_updated=datetime.utcnow(),
            currency=currency_name,
            user_id=current_user.id
        )
        current_app.logger.debug(f"New deposit object: {new_deposit.__dict__}")
        db.session.add(new_deposit)
        db.session.commit()
        flash("Deposit added successfully!!", "success")
        return redirect(url_for("deposit.deposit"))
    else:
        today = datetime.now().strftime("%Y-%m-%d")
        
        currencies = db.session.query(Currency.name, Currency.code).\
            order_by(\
                db.case(\
                    (Currency.name == 'US Dollar', 1),
                    (Currency.name == 'British Pound', 2),
                    (Currency.name == 'Euro', 3),
                    else_=4\
                ),
                Currency.name\
            ).all()
        currencies = [{'code': c.code, 'name': c.name} for c in currencies]

        # Calculate total bankroll and profit for display
        current_poker_total = db.session.query(func.sum(SiteHistory.amount / Currency.rate)).\
            join(Sites, SiteHistory.site_id == Sites.id).\
            join(Currency, SiteHistory.currency == Currency.name).\
            filter(SiteHistory.user_id == current_user.id).\
            filter(SiteHistory.recorded_at == db.session.query(func.max(SiteHistory.recorded_at)).
                   filter_by(site_id=SiteHistory.site_id, user_id=current_user.id)).\
            scalar() or Decimal(0)

        current_asset_total = db.session.query(func.sum(AssetHistory.amount / Currency.rate)).\
            join(Assets, AssetHistory.asset_id == Assets.id).\
            join(Currency, AssetHistory.currency == Currency.name).\
            filter(AssetHistory.user_id == current_user.id).\
            filter(AssetHistory.recorded_at == db.session.query(func.max(AssetHistory.recorded_at)).
                   filter_by(asset_id=AssetHistory.asset_id, user_id=current_user.id)).\
            scalar() or Decimal(0)

        total_withdrawals = db.session.query(func.sum(Drawings.amount / Currency.rate)).\
            join(Currency, Drawings.currency == Currency.name).\
            filter(Drawings.user_id == current_user.id).\
            scalar() or Decimal(0)

        total_deposits = db.session.query(func.sum(Deposits.amount / Currency.rate)).\
            join(Currency, Deposits.currency == Currency.name).\
            filter(Deposits.user_id == current_user.id).\
            scalar() or Decimal(0)

        total_bankroll = current_poker_total + current_asset_total
        total_profit = total_bankroll - total_deposits + total_withdrawals

        return render_template("add_deposit.html", today=today, currencies=currencies, total_profit=total_profit)