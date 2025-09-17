from flask import Blueprint, render_template, redirect, request, url_for, flash, current_app
from datetime import datetime, UTC
from decimal import Decimal
from sqlalchemy import func
from flask_security import login_required, current_user
from ..utils import get_user_bankroll_data, get_sorted_currencies
from ..extensions import db
from ..models import Deposits, Currency

add_deposit_bp = Blueprint("add_deposit", __name__)

@add_deposit_bp.route("/add_deposit", methods=["GET", "POST"])
@login_required
def add_deposit():
    """Add a deposit transaction."""
    if request.method == "POST":
        date_str = request.form.get("date", "")
        amount_str = request.form.get("amount", "")
        currency_code = request.form.get("currency", "USD")

        current_app.logger.debug(f"Form data: date={date_str}, amount={amount_str}, currency={currency_code}")

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
            last_updated=datetime.now(UTC),
            currency=currency_code,
            user_id=current_user.id
        )
        current_app.logger.debug(f"New deposit object: {new_deposit.__dict__}")
        db.session.add(new_deposit)
        db.session.commit()
        flash("Deposit added successfully!!", "success")
        return redirect(url_for("deposit.deposit"))
    else:
        today = datetime.now().strftime("%Y-%m-%d")
        currencies = get_sorted_currencies()
        # Use the centralized utility function to get bankroll data
        bankroll_data = get_user_bankroll_data(current_user.id)
        total_profit = bankroll_data['total_profit']
        default_currency = current_user.default_currency_code if hasattr(current_user, 'default_currency_code') else 'USD'

        return render_template("add_deposit.html", today=today, currencies=currencies, total_profit=total_profit, default_currency=default_currency)