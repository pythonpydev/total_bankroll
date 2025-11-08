# This is a special pytest file used for configuration and defining fixtures/hooks.

import pytest
import os
import sys
from decimal import Decimal

# Add src to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.total_bankroll import create_app
from src.total_bankroll.models import db as _db, User, Currency
from tests.factories import (
    UserFactory, SiteFactory, AssetFactory, DepositFactory, 
    DrawingFactory, CurrencyFactory, create_user_with_bankroll
)


def pytest_addoption(parser):
    """Adds the --num-tests command line option to pytest."""
    parser.addoption(
        "--num-tests",
        action="store",
        default=1,
        type=int,
        help="The number of random hands to select and verify."
    )


def pytest_generate_tests(metafunc):
    """Parametrizes a test to run multiple times based on the --num-tests option."""
    if "iteration" in metafunc.fixturenames:
        num_tests_to_run = metafunc.config.getoption("num_tests")
        metafunc.parametrize("iteration", range(num_tests_to_run))


@pytest.fixture(scope='session')
def app():
    """Create application for testing."""
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret-key',
        'SECURITY_PASSWORD_SALT': 'test-salt',
    })
    
    yield app


@pytest.fixture(scope='function')
def db(app):
    """Provide database for tests with transaction rollback."""
    with app.app_context():
        # Create all tables
        _db.create_all()
        
        # Create base currency if it doesn't exist
        usd = _db.session.query(Currency).filter_by(code='USD').first()
        if not usd:
            usd = Currency(
                id=1,
                code='USD',
                name='US Dollar',
                symbol='$',
                rate=Decimal('1.000000')
            )
            _db.session.add(usd)
            _db.session.commit()
        
        yield _db
        
        # Cleanup
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    """Provide test client."""
    return app.test_client()


@pytest.fixture
def user(db):
    """Create a basic test user."""
    user = UserFactory()
    db.session.commit()
    return user


@pytest.fixture
def user_with_data(db):
    """Create user with sites, assets, deposits, and drawings."""
    return create_user_with_bankroll(
        sites_count=2,
        assets_count=1,
        deposits_count=3,
        drawings_count=1
    )


@pytest.fixture
def authenticated_client(client, user):
    """Provide authenticated test client."""
    with client.session_transaction() as sess:
        sess['user_id'] = user.id
    return client


@pytest.fixture
def currency_usd(db):
    """Provide USD currency."""
    return db.session.get(Currency, 1)


@pytest.fixture
def currency_eur(db):
    """Create EUR currency."""
    eur = CurrencyFactory(
        code='EUR',
        name='Euro',
        symbol='€',
        rate=Decimal('0.920000')
    )
    db.session.commit()
    return eur
