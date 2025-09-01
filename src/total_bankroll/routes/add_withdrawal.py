from flask import Blueprint, render_template, redirect, request, url_for, flash, current_app
from flask_security import login_required, current_user
from datetime import datetime
from decimal import Decimal
from sqlalchemy import func
from ..utils import get_user_bankroll_data, get_sorted_currencies
from ..extensions import db
from ..models import Drawings  # Add this import

add_withdrawal_bp = Blueprint("add_withdrawal", __name__)

@add_withdrawal_bp.route("/add_withdrawal", methods=["GET", "POST"])
@login_required
def add_withdrawal():
    """Add a withdrawal transaction."""
    if request.method == "POST":
        date_str = request.form.get("date", "")
        amount_str = request.form.get("amount", "")
        currency_code = request.form.get("currency", "USD")

        if not date_str or not amount_str:
            flash("Date and amount are required", "danger")
            return redirect(url_for("withdrawal.withdrawal"))

        try:
            date = datetime.strptime(date_str, "%Y-%m-%d")
            amount = round(Decimal(amount_str), 2)
            if amount <= 0:
                flash("Amount must be positive", "danger")
                return redirect(url_for("withdrawal.withdrawal"))
        except ValueError:
            flash("Invalid date or amount format", "danger")
            return redirect(url_for("withdrawal.withdrawal"))

        new_drawing = Drawings(
            date=date,
            amount=amount,
            last_updated=datetime.utcnow(),
            currency=currency_code,
            user_id=current_user.id
        )
        current_app.logger.debug(f"Adding withdrawal for user_id: {current_user.id}")
        db.session.add(new_drawing)
        db.session.commit()
        flash("Withdrawal added successfully!", "success")
        return redirect(url_for("withdrawal.withdrawal"))
    else:
        today = datetime.now().strftime("%Y-%m-%d")
        currencies = get_sorted_currencies()
        # Use the centralized utility function to get bankroll data
        bankroll_data = get_user_bankroll_data(current_user.id)
        total_profit = bankroll_data['total_profit']
        total_bankroll = bankroll_data['total_bankroll']

        current_app.logger.debug(f"Total Bankroll passed to template: {total_bankroll}")
        return render_template("add_withdrawal.html", today=today, currencies=currencies, total_profit=total_profit, total_bankroll=total_bankroll)