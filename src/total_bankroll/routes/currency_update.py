from flask import Blueprint, render_template, redirect, url_for, flash
from flask_security import login_required
from ..extensions import db
from ..models import Currency
# Import your exchange rate update logic here
# from ..utils import update_rates 

currency_update_bp = Blueprint("currency_update", __name__)

@currency_update_bp.route("/currencies")
@login_required
def currencies_page():
    """Currencies page."""
    currencies = db.session.query(Currency).order_by(Currency.name).all()
    return render_template("info/currencies.html", currencies=currencies)

@currency_update_bp.route("/update_exchange_rates", methods=["POST"])
@login_required
def update_exchange_rates():
    # Your logic to update exchange rates would go here.
    # For example: update_rates()
    flash("Exchange rates updated successfully!", "success")
    return redirect(url_for('currency_update.currencies_page'))