from decimal import Decimal
from flask_security import current_user
from .extensions import db
from .models import Sites, SiteHistory, Assets, AssetHistory, Currency, Deposits, Drawings

def get_user_bankroll_data(user_id):
    current_poker_total = Decimal('0')
    previous_poker_total = Decimal('0')
    current_asset_total = Decimal('0')
    previous_asset_total = Decimal('0')

    # Get current and previous poker site totals
    poker_sites_raw_data = (db.session.query(
        Sites.id,
        Sites.name,
        SiteHistory.amount,
        SiteHistory.currency,
        SiteHistory.recorded_at
    ).join(SiteHistory, Sites.id == SiteHistory.site_id)
    .filter(Sites.user_id == user_id)
    .order_by(SiteHistory.recorded_at.desc())
    .all())

    poker_sites_data = {}
    for row in poker_sites_raw_data:
        site_id = row.id
        if site_id not in poker_sites_data:
            poker_sites_data[site_id] = {
                'name': row.name,
                'current_amount': Decimal(str(row.amount)),
                'current_currency': row.currency,
                'previous_amount': Decimal('0'),
                'previous_currency': "US Dollar"
            }
        elif poker_sites_data[site_id]['previous_amount'] == Decimal('0'):
            poker_sites_data[site_id]['previous_amount'] = Decimal(str(row.amount))
            poker_sites_data[site_id]['previous_currency'] = row.currency

    # Get currency rates
    currency_rates_query = db.session.query(Currency.name, Currency.rate).all()
    currency_rates = {row.name: Decimal(str(row.rate)) for row in currency_rates_query}

    for site_id, data in poker_sites_data.items():
        current_rate = currency_rates.get(data['current_currency'], Decimal('1.0'))
        previous_rate = currency_rates.get(data['previous_currency'], Decimal('1.0'))
        current_poker_total += data['current_amount'] / current_rate
        previous_poker_total += data['previous_amount'] / previous_rate

    # Get current and previous asset totals
    assets_raw_data = (db.session.query(
        Assets.id,
        Assets.name,
        AssetHistory.amount,
        AssetHistory.currency,
        AssetHistory.recorded_at
    ).join(AssetHistory, Assets.id == AssetHistory.asset_id)
    .filter(Assets.user_id == user_id)
    .order_by(AssetHistory.recorded_at.desc())
    .all())

    assets_data = {}
    for row in assets_raw_data:
        asset_id = row.id
        if asset_id not in assets_data:
            assets_data[asset_id] = {
                'current_amount': Decimal(str(row.amount)),
                'current_currency': row.currency,
                'previous_amount': Decimal('0'),
                'previous_currency': "US Dollar"
            }
        elif assets_data[asset_id]['previous_amount'] == Decimal('0'):
            assets_data[asset_id]['previous_amount'] = Decimal(str(row.amount))
            assets_data[asset_id]['previous_currency'] = row.currency

    for asset_id, data in assets_data.items():
        current_rate = currency_rates.get(data['current_currency'], Decimal('1.0'))
        previous_rate = currency_rates.get(data['previous_currency'], Decimal('1.0'))
        current_asset_total += data['current_amount'] / current_rate
        previous_asset_total += data['previous_amount'] / previous_rate

    # Get current total of all withdrawals
    total_withdrawals = (db.session.query(db.func.sum(Drawings.amount / Currency.rate))
        .join(Currency, Drawings.currency == Currency.name)
        .filter(Drawings.user_id == user_id)
        .scalar() or Decimal('0'))

    # Get current total of all deposits
    total_deposits = (db.session.query(db.func.sum(Deposits.amount / Currency.rate))
        .join(Currency, Deposits.currency == Currency.name)
        .filter(Deposits.user_id == user_id)
        .scalar() or Decimal('0'))

    total_bankroll = current_poker_total + current_asset_total
    total_profit = total_bankroll - total_deposits + total_withdrawals

    return {
        "current_poker_total": current_poker_total,
        "previous_poker_total": previous_poker_total,
        "current_asset_total": current_asset_total,
        "previous_asset_total": previous_asset_total,
        "total_withdrawals": total_withdrawals,
        "total_deposits": total_deposits,
        "total_bankroll": total_bankroll,
        "total_profit": total_profit
    }
