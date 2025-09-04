from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_security import login_required, current_user
from sqlalchemy.orm import aliased
from sqlalchemy import func, and_, inspect
from decimal import Decimal
from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length

from ..extensions import db
from ..models import Assets, AssetHistory, Currency
from ..utils import get_sorted_currencies
from datetime import datetime

assets_bp = Blueprint("assets", __name__)

class AddAssetForm(FlaskForm):
    name = StringField('Asset Name', validators=[DataRequired(), Length(min=2, max=50)])
    amount = DecimalField('Initial Amount', validators=[DataRequired()])
    currency = SelectField('Currency', coerce=str, validators=[DataRequired()])
    submit = SubmitField('Add Asset')

class UpdateAssetForm(FlaskForm):
    amount = DecimalField('New Amount', validators=[DataRequired()])
    submit = SubmitField('Update Amount')

class RenameAssetForm(FlaskForm):
    name = StringField('New Asset Name', validators=[DataRequired(), Length(min=2, max=50)])
    submit = SubmitField('Rename')

@assets_bp.route("/assets")
@login_required
def assets_page():
    """Assets page."""
    # Efficiently query for assets and their last two history records
    history_ranked = db.session.query(
        AssetHistory,
        func.row_number().over(
            partition_by=AssetHistory.asset_id,
            order_by=AssetHistory.recorded_at.desc()
        ).label('rn')
    ).filter(AssetHistory.user_id == current_user.id).subquery()

    current_history = aliased(history_ranked)
    previous_history = aliased(history_ranked)

    assets_query = db.session.query(
        Assets,
        current_history.c.amount.label('current_amount'),
        current_history.c.currency.label('current_currency_code'),
        previous_history.c.amount.label('previous_amount'),
        previous_history.c.currency.label('previous_currency_code'),
    ).outerjoin(current_history, (Assets.id == current_history.c.asset_id) & (current_history.c.rn == 1))\
     .outerjoin(previous_history, (Assets.id == previous_history.c.asset_id) & (previous_history.c.rn == 2))\
     .filter(Assets.user_id == current_user.id)\
     .order_by(Assets.display_order)

    # Join with Currency table to get rates and symbols
    assets_with_data = []
    total_current = Decimal('0.0')
    total_previous = Decimal('0.0')

    # Pre-fetch all currencies to avoid querying in a loop
    all_currencies = {c.code: c for c in db.session.query(Currency).all()}

    for asset, current_amount, current_currency_code, previous_amount, previous_currency_code in assets_query:
        curr_currency_obj = all_currencies.get(current_currency_code)
        prev_currency_obj = all_currencies.get(previous_currency_code)

        current_amount_usd = (current_amount / curr_currency_obj.rate) if current_amount and curr_currency_obj else Decimal('0.0')
        previous_amount_usd = (previous_amount / prev_currency_obj.rate) if previous_amount and prev_currency_obj else None

        total_current += current_amount_usd
        total_previous += previous_amount_usd if previous_amount_usd is not None else 0

        assets_with_data.append({
            'id': asset.id, 'name': asset.name, 'currency': current_currency_code,
            'currency_symbol': curr_currency_obj.symbol if curr_currency_obj else '',
            'current_amount': current_amount or Decimal('0.0'), 'current_amount_usd': current_amount_usd,
            'previous_amount_usd': previous_amount_usd
        })

    return render_template("assets.html", assets=assets_with_data, total_current=total_current, total_previous=total_previous)

@assets_bp.route("/add_asset", methods=['GET', 'POST'])
@login_required
def add_asset():
    form = AddAssetForm()
    form.currency.choices = [(c['code'], c['name']) for c in get_sorted_currencies()]
    if form.validate_on_submit():
        new_asset = Assets(name=form.name.data, user_id=current_user.id)
        db.session.add(new_asset)
        db.session.flush()  # Get new_asset.id

        initial_history = AssetHistory(
            asset_id=new_asset.id,
            amount=form.amount.data,
            currency=form.currency.data,
            user_id=current_user.id
        )
        db.session.add(initial_history)
        db.session.commit()
        flash('Asset added successfully!', 'success')
        return redirect(url_for('assets.assets_page'))
    return render_template("_modal_form.html", form=form, title="Add New Asset")

@assets_bp.route("/update_asset/<int:asset_id>", methods=['GET', 'POST'])
@login_required
def update_asset(asset_id):
    asset = Assets.query.get_or_404(asset_id)
    if asset.user_id != current_user.id:
        flash('Not authorized to update this asset.', 'danger')
        return redirect(url_for('assets.assets_page'))

    form = UpdateAssetForm()
    last_history = AssetHistory.query.filter_by(asset_id=asset.id, user_id=current_user.id).order_by(AssetHistory.recorded_at.desc()).first()

    if form.validate_on_submit():
        currency_code = last_history.currency if last_history else 'USD'
        new_history = AssetHistory(asset_id=asset.id, amount=form.amount.data, currency=currency_code, user_id=current_user.id)
        db.session.add(new_history)
        db.session.commit()
        flash('Asset amount updated!', 'success')
        return redirect(url_for('assets.assets_page'))
    
    if last_history:
        form.amount.data = last_history.amount

    return render_template("_modal_form.html", form=form, title=f"Update {asset.name}")

@assets_bp.route("/rename_asset/<int:asset_id>", methods=['GET', 'POST'])
@login_required
def rename_asset(asset_id):
    asset = Assets.query.get_or_404(asset_id)
    if asset.user_id != current_user.id:
        flash('Not authorized to rename this asset.', 'danger')
        return redirect(url_for('assets.assets_page'))

    form = RenameAssetForm(obj=asset)
    if form.validate_on_submit():
        asset.name = form.name.data
        db.session.commit()
        flash('Asset renamed successfully!', 'success')
        return redirect(url_for('assets.assets_page'))
    return render_template("_modal_form.html", form=form, title=f"Rename {asset.name}")

@assets_bp.route("/asset_history/<int:asset_id>")
@login_required
def asset_history(asset_id):
    asset = Assets.query.get_or_404(asset_id)
    if asset.user_id != current_user.id:
        flash('Not authorized to view this history.', 'danger')
        return redirect(url_for('assets.assets_page'))

    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')

    history_query = AssetHistory.query.filter_by(asset_id=asset_id, user_id=current_user.id)

    if start_date_str:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        history_query = history_query.filter(AssetHistory.recorded_at >= start_date)
    if end_date_str:
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        end_date = end_date.replace(hour=23, minute=59, second=59)
        history_query = history_query.filter(AssetHistory.recorded_at <= end_date)

    history_raw = history_query.order_by(AssetHistory.recorded_at.desc()).all()

    all_currencies = {c.code: c for c in db.session.query(Currency).all()}
    history_data = []
    for record in history_raw:
        record_dict = {c.key: getattr(record, c.key) for c in inspect(record).mapper.column_attrs}
        currency_obj = all_currencies.get(record.currency)
        record_dict['currency_symbol'] = currency_obj.symbol if currency_obj else ''
        record_dict['currency_name'] = currency_obj.name if currency_obj else record.currency
        history_data.append(record_dict)

    return render_template("asset_history.html", asset=asset, history=history_data, start_date=start_date_str, end_date=end_date_str)

@assets_bp.route('/move_asset/<int:asset_id>/<direction>')
@login_required
def move_asset(asset_id, direction):
    asset_to_move = Assets.query.get_or_404(asset_id)
    if asset_to_move.user_id != current_user.id:
        flash('Not authorized.', 'danger')
        return redirect(url_for('assets.assets_page'))

    assets = Assets.query.filter_by(user_id=current_user.id).order_by(Assets.display_order).all()
    asset_index = assets.index(asset_to_move)

    if direction == 'up' and asset_index > 0:
        swap_with = assets[asset_index - 1]
        asset_to_move.display_order, swap_with.display_order = swap_with.display_order, asset_to_move.display_order
    elif direction == 'down' and asset_index < len(assets) - 1:
        swap_with = assets[asset_index + 1]
        asset_to_move.display_order, swap_with.display_order = swap_with.display_order, asset_to_move.display_order
    else:
        flash('Cannot move asset further.', 'info')
        return redirect(url_for('assets.assets_page'))

    db.session.commit()
    flash(f'{asset_to_move.name} moved.', 'success')
    return redirect(url_for('assets.assets_page'))

@assets_bp.route("/edit_asset_history/<int:history_id>", methods=['GET', 'POST'])
@login_required
def edit_asset_history(history_id):
    history_record = AssetHistory.query.get_or_404(history_id)
    if history_record.user_id != current_user.id:
        flash('Not authorized.', 'danger')
        return redirect(url_for('assets.assets_page'))

    if request.method == 'POST':
        history_record.recorded_at = datetime.strptime(request.form['recorded_at'], '%Y-%m-%d %H:%M:%S')
        history_record.amount = Decimal(request.form['amount'])
        history_record.currency = request.form['currency']
        db.session.commit()
        flash('History record updated successfully!', 'success')
        return redirect(url_for('assets.asset_history', asset_id=history_record.asset_id))

    currencies = get_sorted_currencies()
    return render_template('edit_asset_history.html', history_record=history_record, currencies=currencies)