"""
Factory Boy factories for creating test data.

Provides factories for all models to simplify test data creation.
"""

import factory
from factory import fuzzy
from decimal import Decimal
from datetime import datetime, timedelta
from faker import Faker

from src.total_bankroll.models import (
    db, User, Sites, Assets, Deposits, Drawings, 
    SiteHistory, AssetHistory, Currency
)

fake = Faker()


class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for creating User instances."""
    
    class Meta:
        model = User
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'
    
    email = factory.LazyAttribute(lambda _: fake.unique.email())
    password_hash = '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5ZKaUTRMAeJnS'  # "password"
    active = True
    is_confirmed = True
    confirmed_on = factory.LazyFunction(datetime.now)
    fs_uniquifier = factory.LazyAttribute(lambda _: fake.uuid4())


class CurrencyFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for creating Currency instances."""
    
    class Meta:
        model = Currency
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'
    
    code = factory.Sequence(lambda n: f'C{n:02d}')
    name = factory.LazyAttribute(lambda obj: f'{obj.code} Currency')
    symbol = factory.LazyAttribute(lambda obj: obj.code[0])
    rate = fuzzy.FuzzyDecimal(0.5, 2.0, precision=6)
    updated_at = factory.LazyFunction(datetime.now)


class SiteFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for creating Site instances."""
    
    class Meta:
        model = Sites
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'
    
    user = factory.SubFactory(UserFactory)
    site_name = factory.LazyAttribute(lambda _: f"{fake.company()} Poker")
    balance = fuzzy.FuzzyDecimal(0, 10000, precision=2)
    currency_id = 1  # USD
    last_updated = factory.LazyFunction(datetime.now)


class AssetFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for creating Asset instances."""
    
    class Meta:
        model = Assets
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'
    
    user = factory.SubFactory(UserFactory)
    asset_name = factory.LazyAttribute(lambda _: fake.word().capitalize())
    value = fuzzy.FuzzyDecimal(0, 5000, precision=2)
    currency_id = 1  # USD
    last_updated = factory.LazyFunction(datetime.now)


class DepositFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for creating Deposit instances."""
    
    class Meta:
        model = Deposits
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'
    
    user = factory.SubFactory(UserFactory)
    amount = fuzzy.FuzzyDecimal(50, 500, precision=2)
    currency_id = 1  # USD
    date = factory.LazyFunction(datetime.now)
    notes = factory.LazyAttribute(lambda _: fake.sentence())


class DrawingFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for creating Drawing (withdrawal) instances."""
    
    class Meta:
        model = Drawings
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'
    
    user = factory.SubFactory(UserFactory)
    amount = fuzzy.FuzzyDecimal(50, 500, precision=2)
    currency_id = 1  # USD
    date = factory.LazyFunction(datetime.now)
    notes = factory.LazyAttribute(lambda _: fake.sentence())


class SiteHistoryFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for creating SiteHistory instances."""
    
    class Meta:
        model = SiteHistory
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'
    
    user = factory.SubFactory(UserFactory)
    site = factory.SubFactory(SiteFactory)
    balance = fuzzy.FuzzyDecimal(0, 10000, precision=2)
    recorded_at = factory.LazyFunction(datetime.now)


class AssetHistoryFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for creating AssetHistory instances."""
    
    class Meta:
        model = AssetHistory
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'
    
    user = factory.SubFactory(UserFactory)
    asset = factory.SubFactory(AssetFactory)
    value = fuzzy.FuzzyDecimal(0, 5000, precision=2)
    recorded_at = factory.LazyFunction(datetime.now)


# Helper functions for creating test scenarios

def create_user_with_bankroll(
    sites_count=2,
    assets_count=1,
    deposits_count=3,
    drawings_count=1
):
    """
    Create a complete test user with sites, assets, deposits, and drawings.
    
    Args:
        sites_count: Number of poker sites to create
        assets_count: Number of assets to create
        deposits_count: Number of deposits to create
        drawings_count: Number of withdrawals to create
    
    Returns:
        User instance with associated data
    """
    user = UserFactory()
    
    # Create sites
    sites = [SiteFactory(user=user) for _ in range(sites_count)]
    
    # Create assets
    assets = [AssetFactory(user=user) for _ in range(assets_count)]
    
    # Create deposits
    deposits = [DepositFactory(user=user) for _ in range(deposits_count)]
    
    # Create drawings
    drawings = [DrawingFactory(user=user) for _ in range(drawings_count)]
    
    db.session.commit()
    
    return user


def create_historical_data(user, site=None, asset=None, days_back=30):
    """
    Create historical balance/value data for testing charts.
    
    Args:
        user: User instance
        site: Site instance (if creating site history)
        asset: Asset instance (if creating asset history)
        days_back: Number of days of history to create
    
    Returns:
        List of history instances
    """
    history_records = []
    
    if site:
        for i in range(days_back):
            date = datetime.now() - timedelta(days=days_back - i)
            balance = Decimal(str(1000 + i * 10))  # Gradually increasing
            record = SiteHistoryFactory(
                user=user,
                site=site,
                balance=balance,
                recorded_at=date
            )
            history_records.append(record)
    
    if asset:
        for i in range(days_back):
            date = datetime.now() - timedelta(days=days_back - i)
            value = Decimal(str(500 + i * 5))  # Gradually increasing
            record = AssetHistoryFactory(
                user=user,
                asset=asset,
                value=value,
                recorded_at=date
            )
            history_records.append(record)
    
    db.session.commit()
    return history_records
