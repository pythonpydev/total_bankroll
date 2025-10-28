from flask import Blueprint, render_template, redirect, request, url_for, flash, current_app
from datetime import datetime, UTC
from decimal import Decimal
from sqlalchemy import func
from flask_security import login_required, current_user
from ..achievements import update_user_streak
from ..models import db, Deposits, Currency

add_deposit_bp = Blueprint("add_deposit", __name__)

@add_deposit_bp.route("/add_deposit", methods=["GET", "POST"])
@login_required
def add_deposit():
    """Add a deposit transaction."""
    today = datetime.now().strftime("%Y-%m-%d")
    currencies = get_sorted_currencies()
    default_currency = current_user.default_currency_code if hasattr(current_user, 'default_currency_code') else 'USD'
    current_app.logger.debug(f"DEBUG: In add_deposit route. current_user.default_currency_code: {current_user.default_currency_code}")
    current_app.logger.debug(f"DEBUG: In add_deposit route. default_currency (after check): {default_currency}")
    current_app.logger.debug(f"DEBUG: In add_deposit route. Currencies list: {currencies}")

    if request.method == "POST":
        date_str = request.form.get("date", "")
        amount_str = request.form.get("amount", "")
        currency_code = request.form.get("currency", "USD")

        if not date_str or not amount_str:
            flash("Date and amount are required", "danger")
            return render_template("forms/add_deposit.html", today=today, currencies=currencies, default_currency=default_currency)

        try:
            date = datetime.strptime(date_str, "%Y-%m-%d")
            amount = round(Decimal(amount_str), 2)
            if amount <= 0:
                flash("Amount must be positive", "danger")
                return render_template("forms/add_deposit.html", today=today, currencies=currencies, default_currency=default_currency)
        except ValueError as e:
            flash(f"Invalid date or amount format: {e}", "danger")
            return render_template("forms/add_deposit.html", today=today, currencies=currencies, default_currency=default_currency)

        new_deposit = Deposits(
            date=date,
            amount=amount,
            last_updated=datetime.now(UTC),
            currency=currency_code,
            user_id=current_user.id
        )
        db.session.add(new_deposit)
        db.session.commit()
        update_user_streak(current_user)
        flash("Deposit added successfully!!", "success")
        return redirect(url_for("deposit.deposit"))
    else:
        # GET request
        return render_template("forms/add_deposit.html", today=today, currencies=currencies, default_currency=default_currency)