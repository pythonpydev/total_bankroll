import pytest
from total_bankroll import create_app
from total_bankroll.extensions import db as _db
from total_bankroll.models import User
from total_bankroll.models import Currency
import os

@pytest.fixture(scope='session')
def app():
    """
    Create and configure a new app instance for each test session.
    """
    # By passing the config_name, we ensure the app is created with test settings
    app = create_app(config_name='testing')

    with app.app_context():
        yield app

@pytest.fixture()
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture(scope='function')
def db(app):
    """
    Function-scoped database fixture.
    Creates all tables before each test and drops them afterwards.
    """
    with app.app_context():
        _db.create_all()

        # Add initial currency data for tests
        currencies_to_add = [
            Currency(name='US Dollar', rate=1.0, code='USD', symbol='$'),
            Currency(name='British Pound', rate=0.85, code='GBP', symbol='£'),
            Currency(name='Euro', rate=0.92, code='EUR', symbol='€'),
        ]
        _db.session.add_all(currencies_to_add)
        _db.session.commit()

        yield _db
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def new_user(db):
    """
    Create a new user and save it to the database.
    """
    user = User(
        email='test@example.com',
        password='password123',
        fs_uniquifier=os.urandom(16).hex(),
        active=True,
        is_confirmed=True
    )
    db.session.add(user)
    db.session.commit()
    return user