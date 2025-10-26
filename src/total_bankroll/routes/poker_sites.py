from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_security import login_required, current_user
from sqlalchemy.orm import aliased
from sqlalchemy import func, and_, inspect
from decimal import Decimal
from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SelectField, SubmitField, DateTimeField
from wtforms.validators import DataRequired, Length, Optional

from ..extensions import db
from ..models import Sites, SiteHistory, Currency
from ..achievements import update_user_streak
from datetime import datetime, UTC

poker_sites_bp = Blueprint("poker_sites", __name__)

class AddSiteForm(FlaskForm):
    name = StringField('Site Name', validators=[DataRequired(), Length(min=2, max=50)])
    amount = DecimalField('Initial Amount', validators=[DataRequired()])
    currency = SelectField('Currency', coerce=str, validators=[DataRequired()])
    submit = SubmitField('Add Site')

class UpdateSiteForm(FlaskForm):
    amount = DecimalField('New Amount', validators=[DataRequired()])
    submit = SubmitField('Update Amount')

class RenameSiteForm(FlaskForm):
    name = StringField('New Site Name', validators=[DataRequired(), Length(min=2, max=50)])
    submit = SubmitField('Rename')

class EditSiteHistoryForm(FlaskForm):
    recorded_at = DateTimeField('Recorded At (UTC)', format='%Y-%m-%d %H:%M:%S', validators=[DataRequired()])
    amount = DecimalField('Amount', validators=[DataRequired()])
    currency = SelectField('Currency', coerce=str, validators=[DataRequired()])
    submit = SubmitField('Update Record')

@poker_sites_bp.route("/poker_sites")
@login_required
def poker_sites_page():
    """Poker Sites page."""
    # Efficiently query for sites and their last two history records
    history_ranked = db.session.query(
        SiteHistory,
        func.row_number().over(
            partition_by=SiteHistory.site_id,
            order_by=SiteHistory.recorded_at.desc()
        ).label('rn')
    ).filter(SiteHistory.user_id == current_user.id).subquery()

    current_history = aliased(history_ranked)
    previous_history = aliased(history_ranked)

    sites_query = db.session.query(
        Sites,
        current_history.c.amount.label('current_amount'),
        current_history.c.currency.label('current_currency_code'),
        previous_history.c.amount.label('previous_amount'),
        previous_history.c.currency.label('previous_currency_code'),
    ).outerjoin(current_history, (Sites.id == current_history.c.site_id) & (current_history.c.rn == 1))\
     .outerjoin(previous_history, (Sites.id == previous_history.c.site_id) & (previous_history.c.rn == 2))\
     .filter(Sites.user_id == current_user.id)\
     .order_by(Sites.display_order)

    # Join with Currency table to get rates and symbols
    sites_with_data = []
    total_current = Decimal('0.0')
    total_previous = Decimal('0.0')

    # Pre-fetch all currencies to avoid querying in a loop
    all_currencies = {c.code: c for c in db.session.query(Currency).all()}

    for site, current_amount, current_currency_code, previous_amount, previous_currency_code in sites_query:
        curr_currency_obj = all_currencies.get(current_currency_code)
        prev_currency_obj = all_currencies.get(previous_currency_code)

        current_amount_usd = (current_amount / curr_currency_obj.rate) if current_amount and curr_currency_obj else Decimal('0.0')
        previous_amount_usd = (previous_amount / prev_currency_obj.rate) if previous_amount and prev_currency_obj else None

        total_current += current_amount_usd
        total_previous += previous_amount_usd if previous_amount_usd is not None else 0

        sites_with_data.append({
            'id': site.id, 'name': site.name, 'currency': current_currency_code,
            'currency_symbol': curr_currency_obj.symbol if curr_currency_obj else '',
            'current_amount': current_amount or Decimal('0.0'), 'current_amount_usd': current_amount_usd,
            'previous_amount_usd': previous_amount_usd
        })

    return render_template("poker_sites.html", poker_sites=sites_with_data, total_current=total_current, total_previous=total_previous)

@poker_sites_bp.route("/add_site", methods=['GET', 'POST'])
@login_required
def add_site():
    form = AddSiteForm()
    currencies = get_sorted_currencies()
    form.currency.choices = [(c['code'], c['name']) for c in currencies]
    if request.method == 'GET':
        form.currency.data = current_user.default_currency_code

    if form.validate_on_submit():
        new_site = Sites(name=form.name.data, user_id=current_user.id)
        db.session.add(new_site)
        db.session.flush()  # Flush to get the new_site.id

        initial_history = SiteHistory(
            site_id=new_site.id,
            amount=form.amount.data,
            currency=form.currency.data,
            user_id=current_user.id
        )
        db.session.add(initial_history)
        db.session.commit()
        flash('Site added successfully!', 'success')
        return redirect(url_for('poker_sites.poker_sites_page'))
    elif request.method == 'POST':
        # If validation fails, return errors as JSON
        return jsonify({'success': False, 'errors': form.errors}), 400
    return render_template("_modal_form.html", form=form, title="Add New Site", action_url=url_for('poker_sites.add_site'))

@poker_sites_bp.route("/update_site/<int:site_id>", methods=['GET', 'POST'])
@login_required
def update_site(site_id):
    site = db.session.get(Sites, site_id)
    if not site:
        return "Site not found", 404
    if site.user_id != current_user.id:
        flash('Not authorized to update this site.', 'danger')
        return redirect(url_for('poker_sites.poker_sites_page'))

    form = UpdateSiteForm()
    last_history = SiteHistory.query.filter_by(site_id=site.id, user_id=current_user.id).order_by(SiteHistory.recorded_at.desc()).first()

    if form.validate_on_submit():
        currency_code = last_history.currency if last_history else 'USD'
        new_history = SiteHistory(site_id=site.id, amount=form.amount.data, currency=currency_code, user_id=current_user.id)
        db.session.add(new_history)
        db.session.commit()
        update_user_streak(current_user)
        flash('Site amount updated!', 'success')
        return redirect(url_for('poker_sites.poker_sites_page'))
    
    if last_history:
        form.amount.data = last_history.amount

    return render_template("_modal_form.html", form=form, title=f"Update {site.name}")

@poker_sites_bp.route("/rename_site/<int:site_id>", methods=['GET', 'POST'])
@login_required
def rename_site(site_id):
    site = db.session.get(Sites, site_id)
    if not site:
        return "Site not found", 404
    if site.user_id != current_user.id:
        flash('Not authorized to rename this site.', 'danger')
        return redirect(url_for('poker_sites.poker_sites_page'))

    form = RenameSiteForm(obj=site)
    if form.validate_on_submit():
        site.name = form.name.data
        db.session.commit()
        flash('Site renamed successfully!', 'success')
        return redirect(url_for('poker_sites.poker_sites_page'))
    return render_template("_modal_form.html", form=form, title=f"Rename {site.name}")

@poker_sites_bp.route("/site_history/<int:site_id>")
@login_required
def site_history(site_id):
    site = db.session.get(Sites, site_id)
    if not site:
        flash('Site not found.', 'danger')
        return redirect(url_for('poker_sites.poker_sites_page'))
    if site.user_id != current_user.id:
        flash('Not authorized to view this history.', 'danger')
        return redirect(url_for('poker_sites.poker_sites_page'))

    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')

    history_query = SiteHistory.query.filter_by(site_id=site_id, user_id=current_user.id)

    if start_date_str:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        history_query = history_query.filter(SiteHistory.recorded_at >= start_date)
    if end_date_str:
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        # Add time component to include the whole day
        end_date = end_date.replace(hour=23, minute=59, second=59)
        history_query = history_query.filter(SiteHistory.recorded_at <= end_date)

    history_raw = history_query.order_by(SiteHistory.recorded_at.desc()).all()

    # This is a bit inefficient, but we need currency info.
    # A better approach would be to join Currency in the main query.
    all_currencies = {c.code: c for c in db.session.query(Currency).all()}
    history_data = []
    for record in history_raw:
        record_dict = {c.key: getattr(record, c.key) for c in inspect(record).mapper.column_attrs}
        currency_obj = all_currencies.get(record.currency)
        record_dict['currency_symbol'] = currency_obj.symbol if currency_obj else ''
        record_dict['currency_name'] = currency_obj.name if currency_obj else record.currency
        history_data.append(record_dict)

    return render_template("site_history.html", site=site, history=history_data, start_date=start_date_str, end_date=end_date_str)

@poker_sites_bp.route('/move_site/<int:site_id>/<direction>')
@login_required
def move_site(site_id, direction):
    site_to_move = db.session.get(Sites, site_id)
    if not site_to_move:
        return "Site not found", 404
    if site_to_move.user_id != current_user.id:
        flash('Not authorized.', 'danger')
        return redirect(url_for('poker_sites.poker_sites_page'))

    sites = Sites.query.filter_by(user_id=current_user.id).order_by(Sites.display_order).all()
    site_index = sites.index(site_to_move)

    if direction == 'up' and site_index > 0:
        swap_with = sites[site_index - 1]
        site_to_move.display_order, swap_with.display_order = swap_with.display_order, site_to_move.display_order
    elif direction == 'down' and site_index < len(sites) - 1:
        swap_with = sites[site_index + 1]
        site_to_move.display_order, swap_with.display_order = swap_with.display_order, site_to_move.display_order
    else:
        flash('Cannot move site further.', 'info')
        return redirect(url_for('poker_sites.poker_sites_page'))

    db.session.commit()
    flash(f'{site_to_move.name} moved.', 'success')
    return redirect(url_for('poker_sites.poker_sites_page'))

@poker_sites_bp.route("/edit_site_history/<int:history_id>", methods=['GET', 'POST'])
@login_required
def edit_site_history(history_id):
    history_record = db.session.get(SiteHistory, history_id)
    if not history_record:
        flash('History record not found', 'danger')
        return redirect(url_for('poker_sites.poker_sites_page'))
    if history_record.user_id != current_user.id:
        flash('Not authorized.', 'danger')
        return redirect(url_for('poker_sites.poker_sites_page'))

    form = EditSiteHistoryForm(obj=history_record)
    currencies = get_sorted_currencies()
    form.currency.choices = [(c['code'], c['name']) for c in currencies]

    if form.validate_on_submit():
        try:
            history_record.recorded_at = form.recorded_at.data
            history_record.amount = form.amount.data
            history_record.currency = form.currency.data
            db.session.commit()
            flash('History record updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating record: {e}', 'danger')
        return redirect(url_for('poker_sites.site_history', site_id=history_record.site_id))

    if request.method == 'GET':
        form.currency.data = history_record.currency

    return render_template('_modal_form.html', form=form, title="Edit Site History Record")