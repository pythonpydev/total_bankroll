from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_security import login_required, current_user
from sqlalchemy.orm import aliased
from sqlalchemy import func, and_
from decimal import Decimal
from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length

from ..extensions import db
from ..models import Sites, SiteHistory, Currency
from ..utils import get_sorted_currencies

poker_sites_bp = Blueprint("poker_sites", __name__)

class AddSiteForm(FlaskForm):
    name = StringField('Site Name', validators=[DataRequired(), Length(min=2, max=50)])
    currency = SelectField('Currency', coerce=str, validators=[DataRequired()])
    submit = SubmitField('Add Site')

class UpdateSiteForm(FlaskForm):
    amount = DecimalField('New Amount', validators=[DataRequired()])
    submit = SubmitField('Update Amount')

class RenameSiteForm(FlaskForm):
    name = StringField('New Site Name', validators=[DataRequired(), Length(min=2, max=50)])
    submit = SubmitField('Rename')

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
    form.currency.choices = [(c['code'], c['name']) for c in get_sorted_currencies()]
    if form.validate_on_submit():
        new_site = Sites(name=form.name.data, user_id=current_user.id, currency=form.currency.data)
        db.session.add(new_site)
        db.session.commit()
        flash('Site added successfully!', 'success')
        return redirect(url_for('poker_sites.poker_sites_page'))
    return render_template("_modal_form.html", form=form, title="Add New Site")

@poker_sites_bp.route("/update_site/<int:site_id>", methods=['GET', 'POST'])
@login_required
def update_site(site_id):
    site = Sites.query.get_or_404(site_id)
    if site.user_id != current_user.id:
        flash('Not authorized to update this site.', 'danger')
        return redirect(url_for('poker_sites.poker_sites_page'))

    form = UpdateSiteForm()
    if form.validate_on_submit():
        new_history = SiteHistory(site_id=site.id, amount=form.amount.data, currency=site.currency, user_id=current_user.id)
        db.session.add(new_history)
        db.session.commit()
        flash('Site amount updated!', 'success')
        return redirect(url_for('poker_sites.poker_sites_page'))
    return render_template("_modal_form.html", form=form, title=f"Update {site.name}")

@poker_sites_bp.route("/rename_site/<int:site_id>", methods=['GET', 'POST'])
@login_required
def rename_site(site_id):
    site = Sites.query.get_or_404(site_id)
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
    site = Sites.query.get_or_404(site_id)
    if site.user_id != current_user.id:
        flash('Not authorized to view this history.', 'danger')
        return redirect(url_for('poker_sites.poker_sites_page'))
    history = SiteHistory.query.filter_by(site_id=site_id).order_by(SiteHistory.recorded_at.desc()).all()
    return render_template("history.html", item=site, history=history, item_type='site')

@poker_sites_bp.route('/move_site/<int:site_id>/<direction>')
@login_required
def move_site(site_id, direction):
    site_to_move = Sites.query.get_or_404(site_id)
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