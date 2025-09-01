from decimal import Decimal
from flask_security import current_user
from flask import current_app
from itsdangerous import URLSafeTimedSerializer
from .extensions import db
from .models import User, Sites, SiteHistory, Assets, AssetHistory, Currency, Deposits, Drawings

def generate_token(email):
    """Generates a secure, timed token for email confirmation or password reset."""
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=current_app.config['SECURITY_PASSWORD_SALT'])

def confirm_token(token, expiration=3600):
    """Confirms a token and returns the email if valid and not expired."""
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token, salt=current_app.config['SECURITY_PASSWORD_SALT'], max_age=expiration
        )
        return email
    except Exception:
        return False

def is_email_taken(email, current_user_id):
    """Checks if an email is already taken by another user."""
    existing_user = db.session.query(User).filter(User.email == email, User.id != current_user_id).first()
    return existing_user is not None

def get_sorted_currencies():
    """
    Returns a sorted list of currencies, prioritized for dropdown menus.
    """
    currencies_query = db.session.query(Currency.name, Currency.code).order_by(
        db.case(
            (Currency.name == 'US Dollar', 1),
            (Currency.name == 'British Pound', 2),
            (Currency.name == 'Euro', 3),
            else_=4
        ),
        Currency.name
    ).all()
    return [{'code': c.code, 'name': c.name} for c in currencies_query]

def get_user_bankroll_data(user_id):
    # Get currency rates
    currency_rates_query = db.session.query(Currency.code, Currency.rate).all()
    currency_rates = {row.code: Decimal(str(row.rate)) for row in currency_rates_query}

    def get_latest_history_total(model, history_model, join_column):
        """Helper to get the total USD value of the latest history for a given model."""
        # Subquery to find the latest recorded_at for each item
        latest_history_sq = db.session.query(
            history_model.user_id,
            join_column,
            db.func.max(history_model.recorded_at).label('max_recorded_at')
        ).filter(history_model.user_id == user_id).group_by(join_column).subquery()

        # Join to get the full latest history records
        latest_records = db.session.query(history_model).join(
            latest_history_sq,
            db.and_(
                history_model.user_id == latest_history_sq.c.user_id,
                join_column == latest_history_sq.c[join_column.name],
                history_model.recorded_at == latest_history_sq.c.max_recorded_at
            )
        ).all()

        total_usd = Decimal('0')
        for record in latest_records:
            rate = currency_rates.get(record.currency, Decimal('1.0'))
            total_usd += record.amount / rate
        return total_usd

    # For previous totals, we can adapt the logic from assets.py/poker_sites.py if needed,
    # but for now, we focus on the main bankroll calculation.
    # This simplified version will not calculate previous totals to avoid complexity.
    previous_poker_total = Decimal('0')
    previous_asset_total = Decimal('0')

    current_poker_total = get_latest_history_total(Sites, SiteHistory, SiteHistory.site_id)
    current_asset_total = get_latest_history_total(Assets, AssetHistory, AssetHistory.asset_id)

    # Get current total of all withdrawals
    total_withdrawals = (db.session.query(db.func.sum(Drawings.amount / Currency.rate))
        .join(Currency, Drawings.currency == Currency.code)
        .filter(Drawings.user_id == user_id)
        .scalar() or Decimal('0'))

    # Get current total of all deposits
    total_deposits = (db.session.query(db.func.sum(Deposits.amount / Currency.rate))
        .join(Currency, Deposits.currency == Currency.code)
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
