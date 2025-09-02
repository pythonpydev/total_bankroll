from flask import Blueprint, render_template, redirect, request, url_for, flash
from flask_security import login_required, current_user
from datetime import datetime
from decimal import Decimal
from sqlalchemy import func
from ..utils import get_sorted_currencies 
from ..extensions import db
from ..models import Assets, AssetHistory, Currency

assets_bp = Blueprint("assets", __name__)

@assets_bp.route("/assets")
@login_required
def assets_page():
    """Assets page."""
    currency_data = db.session.query(Currency).all()
    currency_rates = {row.code: Decimal(str(row.rate)) for row in currency_data}
    currency_symbols = {row.code: row.symbol for row in currency_data}
    currency_names = {row.code: row.name for row in currency_data}

    assets = db.session.query(Assets).filter_by(user_id=current_user.id).order_by(Assets.name).all()
    asset_ids = [asset.id for asset in assets]

    # Efficiently fetch the latest two history records for all assets in one query
    if asset_ids:
        from sqlalchemy.orm import aliased
        h2 = aliased(AssetHistory)
        subq = (
            db.session.query(
                AssetHistory,
                func.row_number()
                .over(
                    partition_by=AssetHistory.asset_id,
                    order_by=AssetHistory.recorded_at.desc(),
                )
                .label("rn"),
            )
            .filter(AssetHistory.asset_id.in_(asset_ids))
            .subquery()
        )
        all_history_records = db.session.query(subq).filter(subq.c.rn <= 2).all()

        # Group history records by asset_id for easy lookup
        history_by_asset = {}
        for record in all_history_records:
            if record.asset_id not in history_by_asset:
                history_by_asset[record.asset_id] = []
            history_by_asset[record.asset_id].append(record)
    else:
        history_by_asset = {}

    assets_data = []
    total_current = Decimal(0)
    total_previous = Decimal(0)

    for asset in assets:
        history_records = history_by_asset.get(asset.id, [])

        current_amount = history_records[0].amount if len(history_records) > 0 else Decimal(0)
        currency_code = history_records[0].currency if len(history_records) > 0 else "USD"
        previous_amount = history_records[1].amount if len(history_records) > 1 else Decimal(0)
        previous_currency_code = history_records[1].currency if len(history_records) > 1 else "USD"

        rate = currency_rates.get(currency_code, Decimal('1.0'))
        previous_rate = currency_rates.get(previous_currency_code, Decimal('1.0'))

        current_amount_usd = current_amount / rate
        previous_amount_usd = previous_amount / previous_rate

        assets_data.append({
            'id': asset.id,
            'name': asset.name,
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

    currencies = get_sorted_currencies()
    return render_template("assets.html", assets=assets_data, currencies=currencies, total_current=total_current, total_previous=total_previous)

@assets_bp.route("/add_asset", methods=["GET", "POST"])
@login_required
def add_asset():
    """Add an asset."""
    if request.method == "POST":
        name = request.form.get("name", "").title()
        amount_str = request.form.get("amount", "")
        currency_input = request.form.get("currency", "USD")

        if not name or not amount_str:
            flash("Name and amount are required", "danger")
            return redirect(url_for("assets.assets_page"))

        try:
            amount = round(Decimal(amount_str), 2)
            if amount <= 0:
                flash("Amount must be positive", "danger")
                return redirect(url_for("assets.assets_page"))
        except ValueError:
            flash("Invalid amount format", "danger")
            return redirect(url_for("assets.assets_page"))

        # Robustly find currency code whether name or code is submitted
        currency = db.session.query(Currency).filter((Currency.code == currency_input) | (Currency.name == currency_input)).first()
        if not currency:
            flash(f"Invalid currency '{currency_input}' specified.", "danger")
            return redirect(url_for("assets.assets_page"))
        currency_code = currency.code

        # Insert into assets table
        new_asset = Assets(name=name, user_id=current_user.id)
        db.session.add(new_asset)
        db.session.flush()  # To get the asset.id before commit

        # Insert into asset_history table
        new_asset_history = AssetHistory(
            asset_id=new_asset.id,
            amount=amount,
            currency=currency_code,
            recorded_at=datetime.utcnow(),
            user_id=current_user.id
        )
        db.session.add(new_asset_history)
        
        db.session.commit()
        flash("Asset added successfully!", "success")
        return redirect(url_for("assets.assets_page"))
    else:
        currencies = get_sorted_currencies()
        default_currency = current_user.default_currency_code if hasattr(current_user, 'default_currency_code') else 'USD'
        return render_template("add_asset.html", currencies=currencies, default_currency=default_currency)

@assets_bp.route("/update_asset/<int:asset_id>", methods=["GET", "POST"])
@login_required
def update_asset(asset_id):
    """Update an asset."""
    asset = db.session.query(Assets).filter_by(id=asset_id, user_id=current_user.id).first()
    if asset is None:
        flash("Asset not found", "danger")
        return redirect(url_for("assets.assets_page"))

    if request.method == "POST":
        amount_str = request.form.get("amount", "")
        currency_code = request.form.get("currency", "USD")

        if not amount_str:
            flash("Amount is required", "danger")
            return redirect(url_for("assets.assets_page"))

        try:
            amount = round(Decimal(amount_str), 2)
            if amount <= 0:
                flash("Amount must be positive", "danger")
                return redirect(url_for("assets.assets_page"))
        except ValueError:
            flash("Invalid amount format", "danger")
            return redirect(url_for("assets.assets_page"))

        new_asset_history = AssetHistory(
            asset_id=asset.id,
            amount=amount,
            currency=currency_code,
            recorded_at=datetime.utcnow(),
            user_id=current_user.id
        )
        db.session.add(new_asset_history)
        db.session.commit()
        flash("Asset updated successfully!", "success")
        return redirect(url_for("assets.assets_page"))
    else:
        # Get the latest two history records to find current and previous amounts
        history_records = db.session.query(AssetHistory).\
            filter_by(asset_id=asset.id, user_id=current_user.id).\
            order_by(AssetHistory.recorded_at.desc()).\
            limit(2).all()

        current_amount = history_records[0].amount if len(history_records) > 0 else Decimal(0)
        current_currency = history_records[0].currency if len(history_records) > 0 else "USD"
        previous_amount = history_records[1].amount if len(history_records) > 1 else Decimal(0)

        currencies = get_sorted_currencies()
        return render_template("update_asset.html", asset=asset, currencies=currencies, previous_amount=previous_amount, current_amount=current_amount, current_currency=current_currency)

@assets_bp.route("/rename_asset/<int:asset_id>", methods=["GET", "POST"])
@login_required
def rename_asset(asset_id):
    """Rename an asset."""
    asset = db.session.query(Assets).filter_by(id=asset_id, user_id=current_user.id).first()
    if asset is None:
        flash("Asset not found", "danger")
        return redirect(url_for("assets.assets_page"))

    if request.method == "POST":
        new_name = request.form.get("new_name", "").title()
        if not new_name:
            flash("New name is required", "danger")
            return redirect(url_for("assets.assets_page"))

        asset.name = new_name
        db.session.commit()
        flash("Asset renamed successfully!", "success")
        return redirect(url_for("assets.assets_page"))
    else:
        return render_template("rename_asset.html", asset=asset)