from flask import Blueprint, render_template, redirect, request, url_for, flash
from flask_security import login_required, current_user
from datetime import datetime
from decimal import Decimal
import logging
from sqlalchemy import func
from ..extensions import db
from ..models import Sites, SiteHistory, Currency

logger = logging.getLogger(__name__)

poker_sites_bp = Blueprint("poker_sites", __name__)

@poker_sites_bp.route("/poker_sites")
@login_required
def poker_sites_page():
    """Poker Sites page."""
    currency_data = db.session.query(Currency.name, Currency.rate, Currency.symbol, Currency.code).all()
    currency_rates = {row.code: Decimal(str(row.rate)) for row in currency_data}
    currency_symbols = {row.code: row.symbol for row in currency_data}
    currency_names = {row.code: row.name for row in currency_data}

    # Get all sites for the user
    sites = db.session.query(Sites).filter_by(user_id=current_user.id).order_by(Sites.name).all()

    poker_sites_data = []
    total_current = Decimal(0)
    total_previous = Decimal(0)

    for site in sites:
        # Get the latest two history records for each site
        history_records = db.session.query(SiteHistory).\
            filter_by(site_id=site.id, user_id=current_user.id).\
            order_by(SiteHistory.recorded_at.desc()).\
            limit(2).all()

        current_amount = Decimal(0)
        previous_amount = Decimal(0)
        currency_code = "USD"
        previous_currency_code = "USD"

        if len(history_records) > 0:
            current_amount = history_records[0].amount
            currency_code = history_records[0].currency
        if len(history_records) > 1:
            previous_amount = history_records[1].amount
            previous_currency_code = history_records[1].currency

        rate = currency_rates.get(currency_code, Decimal('1.0'))
        previous_rate = currency_rates.get(previous_currency_code, Decimal('1.0'))

        current_amount_usd = current_amount / rate
        previous_amount_usd = previous_amount / previous_rate

        poker_sites_data.append({
            'id': site.id,
            'name': site.name,
            'current_amount': current_amount,
            'previous_amount': previous_amount,
            'currency': currency_names.get(currency_code, currency_code),
            'previous_currency': currency_names.get(previous_currency_code, previous_currency_code),
            'current_amount_usd': current_amount_usd,
            'previous_amount_usd': previous_amount_usd,
            'currency_symbol': currency_symbols.get(currency_code, currency_code),
            'previous_currency_symbol': currency_symbols.get(previous_currency_code, previous_currency_code)
        })
        total_current += current_amount_usd
        total_previous += previous_amount_usd

    currencies = db.session.query(Currency.name, Currency.code).\
        order_by(
            db.case(
                (Currency.name == 'US Dollar', 1),
                (Currency.name == 'British Pound', 2),
                (Currency.name == 'Euro', 3),
                else_=4
            ),
            Currency.name
        ).all()

    return render_template("poker_sites.html", poker_sites=poker_sites_data, currencies=currencies, total_current=total_current, total_previous=total_previous)


@poker_sites_bp.route("/add_site", methods=["GET", "POST"])
@login_required
def add_site():
    """Add a poker site."""
    if request.method == "POST":
        name = request.form.get("name", "").title()
        amount_str = request.form.get("amount", "")
        currency_code = request.form.get("currency", "USD")

        if not name or not amount_str:
            flash("Name and amount are required", "danger")
            return redirect(url_for("poker_sites.poker_sites_page"))

        try:
            amount = round(Decimal(amount_str), 2)
            if amount <= 0:
                flash("Amount must be positive", "danger")
                return redirect(url_for("poker_sites.poker_sites_page"))
        except ValueError:
            flash("Invalid amount format", "danger")
            return redirect(url_for("poker_sites.poker_sites_page"))

        # Insert into sites table
        new_site = Sites(name=name, user_id=current_user.id)
        db.session.add(new_site)
        db.session.flush()  # To get the site.id before commit

        # Insert into site_history table
        new_site_history = SiteHistory(
            site_id=new_site.id,
            amount=amount,
            currency=currency_code,
            recorded_at=datetime.utcnow(),
            user_id=current_user.id
        )
        db.session.add(new_site_history)
        
        db.session.commit()
        flash("Site added successfully!", "success")
        return redirect(url_for("poker_sites.poker_sites_page"))
    else:
        currencies = db.session.query(Currency.name, Currency.code).\
            order_by(
                db.case(
                    (Currency.name == 'US Dollar', 1),
                    (Currency.name == 'British Pound', 2),
                    (Currency.name == 'Euro', 3),
                    else_=4
                ),
                Currency.name
            ).all()
        currencies = [{'code': c.code, 'name': c.name} for c in currencies]  # Extract names and codes from objects
        logger.debug(f"Currencies fetched: {currencies}")
        return render_template("add_site.html", currencies=currencies)


@poker_sites_bp.route("/update_site/<int:site_id>", methods=["GET", "POST"])
@login_required
def update_site(site_id):
    """Update a poker site."""
    site = db.session.query(Sites).filter_by(id=site_id, user_id=current_user.id).first()
    if site is None:
        flash("Site not found", "danger")
        return redirect(url_for("poker_sites.poker_sites_page"))

    if request.method == "POST":
        amount_str = request.form.get("amount", "")
        currency_code = request.form.get("currency", "USD")

        if not amount_str:
            flash("Amount is required", "danger")
            return redirect(url_for("poker_sites.poker_sites_page"))

        try:
            amount = round(Decimal(amount_str), 2)
            if amount <= 0:
                flash("Amount must be positive", "danger")
                return redirect(url_for("poker_sites.poker_sites_page"))
        except ValueError:
            flash("Invalid amount format", "danger")
            return redirect(url_for("poker_sites.poker_sites_page"))

        new_site_history = SiteHistory(
            site_id=site.id,
            amount=amount,
            currency=currency_code,
            recorded_at=datetime.utcnow(),
            user_id=current_user.id
        )
        db.session.add(new_site_history)
        db.session.commit()
        flash("Site updated successfully!", "success")
        return redirect(url_for("poker_sites.poker_sites_page"))
    else:
        # Get current amount and currency from site_history
        current_amount_row = db.session.query(SiteHistory).\
            filter_by(site_id=site.id, user_id=current_user.id).\
            order_by(SiteHistory.recorded_at.desc()).\
            first()
        
        current_amount = current_amount_row.amount if current_amount_row else Decimal(0)
        current_currency = current_amount_row.currency if current_amount_row else "USD"

        # Get previous amount (second most recent entry)
        previous_amount_row = db.session.query(SiteHistory).\
            filter_by(site_id=site.id, user_id=current_user.id).\
            order_by(SiteHistory.recorded_at.desc()).\
            offset(1).limit(1).first()
        
        previous_amount = previous_amount_row.amount if previous_amount_row else Decimal(0)

        currencies = db.session.query(Currency.name, Currency.code).            order_by(                db.case(                    (Currency.name == 'US Dollar', 1),
                    (Currency.name == 'British Pound', 2),
                    (Currency.name == 'Euro', 3),
                    else_=4                ),
                Currency.name            ).all()
        currencies = [{'code': c.code, 'name': c.name} for c in currencies]  # Extract names and codes from objects

        return render_template("update_site.html", site=site, currencies=currencies, previous_amount=previous_amount, current_amount=current_amount, current_currency=current_currency)


@poker_sites_bp.route("/rename_site/<int:site_id>", methods=["GET", "POST"])
@login_required
def rename_site(site_id):
    """Rename a poker site."""
    site = db.session.query(Sites).filter_by(id=site_id, user_id=current_user.id).first()
    if site is None:
        flash("Site not found", "danger")
        return redirect(url_for("poker_sites.poker_sites_page"))

    if request.method == "POST":
        new_name = request.form.get("new_name", "").title()
        if not new_name:
            flash("New name is required", "danger")
            return redirect(url_for("poker_sites.poker_sites_page"))

        site.name = new_name
        db.session.commit()
        flash("Site renamed successfully!", "success")
        return redirect(url_for("poker_sites.poker_sites_page"))
    else:
        return render_template("rename_site.html", site=site)