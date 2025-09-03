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
    # One-time data migration for existing assets with no order
    uninitialized_assets = db.session.query(Assets).filter_by(user_id=current_user.id, display_order=0).all()
    if uninitialized_assets:
        max_order = db.session.query(func.max(Assets.display_order)).filter_by(user_id=current_user.id).scalar() or 0
        for i, asset in enumerate(uninitialized_assets):
            asset.display_order = max_order + i + 1
        db.session.commit()

    currency_data = db.session.query(Currency).all()
    currency_rates = {row.code: Decimal(str(row.rate)) for row in currency_data}
    currency_symbols = {row.code: row.symbol for row in currency_data}
    currency_names = {row.code: row.name for row in currency_data}

    assets = db.session.query(Assets).filter_by(user_id=current_user.id).order_by(Assets.display_order).all()
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

        # Determine the display order for the new asset
        max_order = db.session.query(func.max(Assets.display_order)).filter_by(user_id=current_user.id).scalar()
        new_order = (max_order or 0) + 1

        # Insert into assets table
        new_asset = Assets(name=name, 
                           user_id=current_user.id,
                           display_order=new_order)
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

@assets_bp.route("/assets/move/<int:asset_id>/<direction>")
@login_required
def move_asset(asset_id, direction):
    """Move an asset up or down in the display order."""
    if direction not in ['up', 'down']:
        flash("Invalid direction.", "danger")
        return redirect(url_for('assets.assets_page'))

    assets = db.session.query(Assets).filter_by(user_id=current_user.id).order_by(Assets.display_order).all()
    
    asset_to_move_index = -1
    for i, asset in enumerate(assets):
        if asset.id == asset_id:
            asset_to_move_index = i
            break

    if asset_to_move_index == -1:
        flash("Asset not found.", "danger")
    elif direction == 'up' and asset_to_move_index > 0:
        other_asset = assets[asset_to_move_index - 1]
        assets[asset_to_move_index].display_order, other_asset.display_order = other_asset.display_order, assets[asset_to_move_index].display_order
        db.session.commit()
    elif direction == 'down' and asset_to_move_index < len(assets) - 1:
        other_asset = assets[asset_to_move_index + 1]
        assets[asset_to_move_index].display_order, other_asset.display_order = other_asset.display_order, assets[asset_to_move_index].display_order
        db.session.commit()
    
    return redirect(url_for('assets.assets_page'))

@assets_bp.route("/assets/history/<int:asset_id>")
@login_required
def asset_history(asset_id):
    """Display the history for a specific asset."""
    asset = db.session.query(Assets).filter_by(id=asset_id, user_id=current_user.id).first_or_404()
    history = db.session.query(AssetHistory).filter_by(asset_id=asset_id, user_id=current_user.id).order_by(AssetHistory.recorded_at.desc()).all()
    
    currency_data = db.session.query(Currency).all()
    currency_symbols = {row.code: row.symbol for row in currency_data}
    currency_names = {row.code: row.name for row in currency_data}

    history_data = []
    for record in history:
        history_data.append({
            'id': record.id,
            'recorded_at': record.recorded_at.strftime("%Y-%m-%d %H:%M:%S"),
            'amount': record.amount,
            'currency_name': currency_names.get(record.currency, record.currency),
            'currency_symbol': currency_symbols.get(record.currency, record.currency)
        })

    return render_template("asset_history.html", asset=asset, history=history_data)

@assets_bp.route("/assets/history/edit/<int:history_id>", methods=["GET", "POST"])
@login_required
def edit_asset_history(history_id):
    """Edit a specific asset history record."""
    history_record = db.session.query(AssetHistory).filter_by(id=history_id, user_id=current_user.id).first_or_404()
    
    if request.method == "POST":
        amount_str = request.form.get("amount", "")
        currency_code = request.form.get("currency", "USD")
        date_str = request.form.get("recorded_at", "")

        if not amount_str or not date_str:
            flash("Amount and date are required.", "danger")
            return redirect(url_for('assets.asset_history', asset_id=history_record.asset_id))

        try:
            history_record.amount = round(Decimal(amount_str), 2)
            history_record.currency = currency_code
            history_record.recorded_at = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            db.session.commit()
            flash("History record updated successfully!", "success")
        except (ValueError, Exception) as e:
            db.session.rollback()
            flash(f"An error occurred: {e}", "danger")
        
        return redirect(url_for('assets.asset_history', asset_id=history_record.asset_id))
    else:
        # GET request
        currencies = get_sorted_currencies()
        return render_template("edit_asset_history.html", history_record=history_record, currencies=currencies)