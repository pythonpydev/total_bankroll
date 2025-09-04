from .extensions import db
from .models import SiteHistory, AssetHistory, Deposits, Drawings, Currency, User
from sqlalchemy import func, case, literal_column
from decimal import Decimal
from itsdangerous import URLSafeTimedSerializer
from flask import current_app

def get_sorted_currencies():
    """
    Fetches all currencies from the database and returns them as a sorted list of dictionaries.
    """
    currencies = Currency.query.order_by(Currency.name).all()
    return [{'code': c.code, 'name': c.name, 'symbol': c.symbol} for c in currencies]

def get_user_bankroll_data(user_id):
    """
    Calculates all key financial metrics for a user with a single, efficient database query.

    This function uses conditional aggregation to sum up different types of records
    (poker sites, assets, deposits, withdrawals) in one pass, significantly improving
    performance by reducing database round trips.

    Args:
        user_id: The ID of the user for whom to calculate the data.

    Returns:
        A dictionary containing all calculated financial metrics.
    """
    # Subquery to rank site history records for each site
    site_history_ranked = db.session.query(
        SiteHistory,
        func.row_number().over(partition_by=SiteHistory.site_id, order_by=SiteHistory.recorded_at.desc()).label('rn')
    ).filter(SiteHistory.user_id == user_id).subquery()

    # Subquery to rank asset history records for each asset
    asset_history_ranked = db.session.query(
        AssetHistory,
        func.row_number().over(partition_by=AssetHistory.asset_id, order_by=AssetHistory.recorded_at.desc()).label('rn')
    ).filter(AssetHistory.user_id == user_id).subquery()

    # Calculate totals using the ranked subqueries
    current_poker_total = db.session.query(func.sum(site_history_ranked.c.amount / Currency.rate))\
        .select_from(site_history_ranked)\
        .join(Currency, site_history_ranked.c.currency == Currency.code)\
        .filter(site_history_ranked.c.rn == 1).scalar() or Decimal('0.0')
    previous_poker_total = db.session.query(func.sum(site_history_ranked.c.amount / Currency.rate))\
        .select_from(site_history_ranked)\
        .join(Currency, site_history_ranked.c.currency == Currency.code)\
        .filter(site_history_ranked.c.rn == 2).scalar() or Decimal('0.0')
    
    current_asset_total = db.session.query(func.sum(asset_history_ranked.c.amount / Currency.rate))\
        .select_from(asset_history_ranked)\
        .join(Currency, asset_history_ranked.c.currency == Currency.code)\
        .filter(asset_history_ranked.c.rn == 1).scalar() or Decimal('0.0')
    previous_asset_total = db.session.query(func.sum(asset_history_ranked.c.amount / Currency.rate))\
        .select_from(asset_history_ranked)\
        .join(Currency, asset_history_ranked.c.currency == Currency.code)\
        .filter(asset_history_ranked.c.rn == 2).scalar() or Decimal('0.0')

    # Calculate deposit and withdrawal totals
    total_deposits = db.session.query(func.sum(Deposits.amount / Currency.rate))\
        .join(Currency, Deposits.currency == Currency.code)\
        .filter(Deposits.user_id == user_id)\
        .scalar() or Decimal('0.0')

    total_withdrawals = db.session.query(func.sum(Drawings.amount / Currency.rate))\
        .join(Currency, Drawings.currency == Currency.code)\
        .filter(Drawings.user_id == user_id)\
        .scalar() or Decimal('0.0')

    # Calculate derived metrics
    total_bankroll = current_poker_total + current_asset_total
    total_profit = total_bankroll - total_deposits + total_withdrawals

    return {
        'current_poker_total': current_poker_total,
        'previous_poker_total': previous_poker_total,
        'current_asset_total': current_asset_total,
        'previous_asset_total': previous_asset_total,
        'total_deposits': total_deposits,
        'total_withdrawals': total_withdrawals,
        'total_bankroll': total_bankroll,
        'total_profit': total_profit,
    }

def generate_token(email):
    """Generates a secure token for password reset or email confirmation."""
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt='email-confirm-salt')

def confirm_token(token, expiration=3600):
    """
    Verifies the token and returns the email address if valid.
    Handles token expiration.
    """
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt='email-confirm-salt',
            max_age=expiration
        )
        return email
    except Exception:  # includes SignatureExpired, BadSignature
        return False

def is_email_taken(email, current_user_id):
    """
    Checks if an email address is already in use by another user.
    """
    user = User.query.filter(User.email == email, User.id != current_user_id).first()
    return user is not None