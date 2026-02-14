"""Tests for the CSV database export functionality.

Uses an isolated SQLite in-memory database so the real MySQL dev DB is untouched.
"""

import csv
import io
import os
import pytest
from decimal import Decimal
from datetime import datetime, UTC
from uuid import uuid4

from flask_security import login_user

# ---------------------------------------------------------------------------
# Fixtures — self-contained so we don't depend on the global conftest
# (which has outdated factories that reference old column names).
# ---------------------------------------------------------------------------

@pytest.fixture(scope='module')
def export_app():
    """Create a fully isolated Flask app for export tests."""
    # Temporarily override FLASK_ENV to avoid loading MySQL config
    old_env = os.environ.get('FLASK_ENV')
    os.environ['FLASK_ENV'] = 'development'

    from src.total_bankroll import create_app
    app = create_app()

    # Force SQLite in-memory regardless of .env
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret-key-export',
        'SECURITY_PASSWORD_SALT': 'test-salt-export',
        'SECURITY_BLUEPRINT_NAME': 'auth',   # matches auth_bp name
        'SERVER_NAME': 'localhost.localdomain',
    })

    if old_env is not None:
        os.environ['FLASK_ENV'] = old_env

    yield app


@pytest.fixture(autouse=True)
def export_db(export_app):
    """Create tables, seed a currency, yield the db, then tear down."""
    from src.total_bankroll.models import db, Currency

    with export_app.app_context():
        db.create_all()

        usd = db.session.query(Currency).filter_by(code='USD').first()
        if not usd:
            usd = Currency(
                id=1, code='USD', name='US Dollar',
                symbol='$', rate=Decimal('1.000000'),
            )
            db.session.add(usd)
            db.session.commit()

        yield db

        db.session.remove()
        db.drop_all()


@pytest.fixture
def export_client(export_app):
    return export_app.test_client()


@pytest.fixture
def test_user(export_app, export_db):
    """Create a confirmed user and return (user, password)."""
    from src.total_bankroll.models import User

    with export_app.app_context():
        password = 'password123'
        user = User(
            email=f'export_{uuid4().hex[:8]}@test.com',
            active=True,
            is_confirmed=True,
            confirmed_on=datetime.now(UTC),
            fs_uniquifier=uuid4().hex,
            default_currency_code='USD',
        )
        user.password = password
        export_db.session.add(user)
        export_db.session.commit()

        # Eagerly load the id so it survives outside the session
        user_id = user.id
        user_email = user.email

    return user_id, user_email, password


@pytest.fixture
def seeded_user(export_app, export_db, test_user):
    """Create a user with sites, assets, deposits, drawings, and history."""
    from src.total_bankroll.models import (
        Sites, Assets, Deposits, Drawings, SiteHistory, AssetHistory,
    )

    user_id, user_email, password = test_user

    with export_app.app_context():
        site = Sites(name='PokerStars', user_id=user_id, display_order=0)
        export_db.session.add(site)
        export_db.session.flush()

        asset = Assets(name='Bitcoin Wallet', user_id=user_id, display_order=0)
        export_db.session.add(asset)
        export_db.session.flush()

        dep = Deposits(
            date=datetime(2025, 1, 15),
            amount=Decimal('500.00'),
            last_updated=datetime.now(UTC),
            currency='USD',
            user_id=user_id,
        )
        export_db.session.add(dep)

        draw = Drawings(
            date=datetime(2025, 2, 10),
            amount=Decimal('200.00'),
            last_updated=datetime.now(UTC),
            currency='USD',
            user_id=user_id,
        )
        export_db.session.add(draw)

        sh = SiteHistory(
            site_id=site.id,
            amount=Decimal('1500.00'),
            currency='USD',
            recorded_at=datetime.now(UTC),
            user_id=user_id,
        )
        export_db.session.add(sh)

        ah = AssetHistory(
            asset_id=asset.id,
            amount=Decimal('3000.00'),
            currency='USD',
            recorded_at=datetime.now(UTC),
            user_id=user_id,
        )
        export_db.session.add(ah)

        export_db.session.commit()

    return user_id, user_email, password


def _login_user_directly(export_app, export_client, user_id):
    """Log the user in via Flask-Security's login_user (bypasses form)."""
    from src.total_bankroll.models import User

    with export_client.session_transaction():
        pass  # ensure session exists

    with export_app.app_context():
        user = export_app.extensions['security'].datastore.find_user(id=user_id)
        assert user is not None, f"Could not find user with id={user_id}"
        with export_app.test_request_context():
            login_user(user)


# ── Tests ──────────────────────────────────────────────────────────────


def test_export_requires_login(export_client):
    """Export endpoint should redirect or deny unauthenticated users."""
    response = export_client.post('/perform_export_database')
    # Flask-Security may redirect (302) or return 401/403
    assert response.status_code in (302, 401, 403)


def test_export_returns_csv(export_app, export_client, seeded_user):
    """Export should return a downloadable CSV with correct headers."""
    user_id, email, password = seeded_user

    with export_client:
        # Login via the form (matches existing test patterns)
        export_client.post('/login', data={
            'email': email, 'password': password,
        }, follow_redirects=True)

        response = export_client.post('/perform_export_database')

    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}. Body: {response.data[:500]}"
    )
    assert 'text/csv' in response.content_type
    assert 'bankroll_export.csv' in response.headers.get('Content-Disposition', '')


def test_export_csv_contains_all_tables(export_app, export_client, seeded_user):
    """The exported CSV should contain sections for every table with data."""
    user_id, email, password = seeded_user

    with export_client:
        export_client.post('/login', data={
            'email': email, 'password': password,
        }, follow_redirects=True)

        response = export_client.post('/perform_export_database')
        csv_text = response.data.decode('utf-8')

    expected_tables = [
        'sites', 'assets', 'deposits', 'drawings',
        'site_history', 'asset_history', 'currency',
    ]
    for table in expected_tables:
        assert f'Table: {table}' in csv_text, f"Missing 'Table: {table}' in export"


def test_export_csv_columns_match_models(export_app, export_client, seeded_user):
    """CSV headers for each table should match the model's column names."""
    from src.total_bankroll.models import (
        Sites, Assets, Deposits, Drawings,
        SiteHistory, AssetHistory, Currency,
    )

    user_id, email, password = seeded_user

    with export_client:
        export_client.post('/login', data={
            'email': email, 'password': password,
        }, follow_redirects=True)
        response = export_client.post('/perform_export_database')
        csv_text = response.data.decode('utf-8')

    reader = csv.reader(io.StringIO(csv_text))
    rows = list(reader)

    # Build mapping: table_name -> header row
    headers_map = {}
    for i, row in enumerate(rows):
        if row and row[0].startswith('Table: '):
            table_name = row[0].replace('Table: ', '').strip()
            if i + 1 < len(rows):
                headers_map[table_name] = rows[i + 1]

    expected = {
        'sites': [c.name for c in Sites.__table__.columns],
        'assets': [c.name for c in Assets.__table__.columns],
        'deposits': [c.name for c in Deposits.__table__.columns],
        'drawings': [c.name for c in Drawings.__table__.columns],
        'site_history': [c.name for c in SiteHistory.__table__.columns],
        'asset_history': [c.name for c in AssetHistory.__table__.columns],
        'currency': [c.name for c in Currency.__table__.columns],
    }

    for table_name, expected_cols in expected.items():
        assert table_name in headers_map, f"Table '{table_name}' not found in export"
        assert headers_map[table_name] == expected_cols, (
            f"Column mismatch for '{table_name}': "
            f"got {headers_map[table_name]}, expected {expected_cols}"
        )


def test_export_csv_data_values_correct(export_app, export_client, seeded_user):
    """Spot-check that actual data values are present in the CSV."""
    user_id, email, password = seeded_user

    with export_client:
        export_client.post('/login', data={
            'email': email, 'password': password,
        }, follow_redirects=True)
        response = export_client.post('/perform_export_database')
        csv_text = response.data.decode('utf-8')

    assert 'PokerStars' in csv_text
    assert 'Bitcoin Wallet' in csv_text
    assert '500.00' in csv_text   # deposit amount
    assert '200.00' in csv_text   # withdrawal amount
    assert '1500.00' in csv_text  # site history balance
    assert '3000.00' in csv_text  # asset history value


def test_export_csv_is_reimportable(export_app, export_client, seeded_user):
    """Exported CSV should be parseable with the Table:/header/data structure."""
    user_id, email, password = seeded_user

    with export_client:
        export_client.post('/login', data={
            'email': email, 'password': password,
        }, follow_redirects=True)
        response = export_client.post('/perform_export_database')
        csv_text = response.data.decode('utf-8')

    reader = csv.reader(io.StringIO(csv_text))

    tables_found = {}
    current_table = None

    for row in reader:
        if not row:
            current_table = None
            continue
        if row[0].startswith('Table: '):
            current_table = row[0].replace('Table: ', '').strip()
            tables_found[current_table] = {'headers': None, 'row_count': 0}
        elif current_table and tables_found[current_table]['headers'] is None:
            tables_found[current_table]['headers'] = row
        elif current_table:
            tables_found[current_table]['row_count'] += 1
            assert len(row) == len(tables_found[current_table]['headers']), (
                f"Column count mismatch in '{current_table}': "
                f"header has {len(tables_found[current_table]['headers'])}, "
                f"row has {len(row)}"
            )

    # All user-specific tables should have at least one data row
    for t in ['sites', 'assets', 'deposits', 'drawings', 'site_history', 'asset_history', 'currency']:
        assert t in tables_found, f"Table '{t}' missing from export"
        assert tables_found[t]['row_count'] >= 1, f"Table '{t}' has no data rows"


def test_export_import_round_trip(export_app, export_client, seeded_user):
    """
    The ultimate test: export the database, wipe user data, re-import the CSV,
    then export again and compare. Both exports should be identical.
    """
    user_id, email, password = seeded_user

    with export_client:
        export_client.post('/login', data={
            'email': email, 'password': password,
        }, follow_redirects=True)

        # ── Export #1 ──
        resp1 = export_client.post('/perform_export_database')
        assert resp1.status_code == 200, f"Export #1 failed: {resp1.data[:300]}"
        csv_bytes_1 = resp1.data

        # ── Import the CSV back (simulating the Windows machine) ──
        from io import BytesIO
        import_resp = export_client.post(
            '/settings/import_database',
            data={'file': (BytesIO(csv_bytes_1), 'bankroll_export.csv')},
            content_type='multipart/form-data',
        )
        assert import_resp.status_code == 200, (
            f"Import failed: {import_resp.data.decode()}"
        )
        import_json = import_resp.get_json()
        assert import_json['success'] is True, f"Import error: {import_json.get('message')}"

        # ── Export #2 (after import) ──
        resp2 = export_client.post('/perform_export_database')
        assert resp2.status_code == 200, f"Export #2 failed: {resp2.data[:300]}"
        csv_bytes_2 = resp2.data

    # ── Compare the two exports ──
    # Parse both into structured data for comparison (ignore exact whitespace)
    def parse_export(raw_bytes):
        """Parse CSV export into {table: {headers, rows}} for comparison."""
        reader = csv.reader(io.StringIO(raw_bytes.decode('utf-8')))
        tables = {}
        current = None
        for row in reader:
            if not row:
                current = None
                continue
            if row[0].startswith('Table: '):
                current = row[0].replace('Table: ', '').strip()
                tables[current] = {'headers': None, 'rows': []}
            elif current and tables[current]['headers'] is None:
                tables[current]['headers'] = row
            elif current:
                tables[current]['rows'].append(row)
        return tables

    t1 = parse_export(csv_bytes_1)
    t2 = parse_export(csv_bytes_2)

    # Same tables present
    assert set(t1.keys()) == set(t2.keys()), (
        f"Table set mismatch: {set(t1.keys())} vs {set(t2.keys())}"
    )

    # Same headers and same number of rows per table
    for table_name in t1:
        assert t1[table_name]['headers'] == t2[table_name]['headers'], (
            f"Headers differ for '{table_name}'"
        )
        assert len(t1[table_name]['rows']) == len(t2[table_name]['rows']), (
            f"Row count differs for '{table_name}': "
            f"{len(t1[table_name]['rows'])} vs {len(t2[table_name]['rows'])}"
        )

    # Spot-check: the actual data values should survive the round-trip
    csv_text_2 = csv_bytes_2.decode('utf-8')
    assert 'PokerStars' in csv_text_2
    assert 'Bitcoin Wallet' in csv_text_2
    assert '500.00' in csv_text_2
    assert '200.00' in csv_text_2
    assert '1500.00' in csv_text_2
    assert '3000.00' in csv_text_2
