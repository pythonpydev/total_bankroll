import pytest
import os
import tempfile
import sqlite3
from total_bankroll.main import app, get_db, init_db

@pytest.fixture
def client():
    db_fd, db_path = tempfile.mkstemp()
    app.config['DATABASE'] = db_path
    app.config['TESTING'] = True

    with app.test_client() as client:
        with app.app_context():
            init_db()
        yield client

    os.close(db_fd)
    os.unlink(db_path)

def get_bankroll_data(client):
    response = client.get('/')
    html = response.data.decode('utf-8')

    import re

    def extract_row_values(category):
        # Regex to capture previous and current values for a given category row
        pattern = rf"<td>{category}</td>\s*<td>\$\s*(\d+\.\d{{2}})</td>\s*<td>\$\s*(\d+\.\d{{2}})</td>"
        match = re.search(pattern, html)
        if match:
            return float(match.group(1)), float(match.group(2))
        return 0.0, 0.0

    previous_poker_total, current_poker_total = extract_row_values("Poker Sites")
    previous_asset_total, current_asset_total = extract_row_values("Assets")
    previous_withdrawal_total, current_withdrawal_total = extract_row_values("Withdrawal")
    previous_deposit_total, current_deposit_total = extract_row_values("Deposits")
    previous_net_worth, total_net_worth = extract_row_values("Total Net Worth")
    previous_profit, current_profit = extract_row_values("Profit")

    return {
        "current_poker_total": current_poker_total,
        "previous_poker_total": previous_poker_total,
        "current_asset_total": current_asset_total,
        "previous_asset_total": previous_asset_total,
        "current_withdrawal_total": current_withdrawal_total,
        "previous_withdrawal_total": previous_withdrawal_total,
        "current_deposit_total": current_deposit_total,
        "previous_deposit_total": previous_deposit_total,
        "total_net_worth": total_net_worth,
        "previous_net_worth": previous_net_worth,
        "current_profit": current_profit,
        "previous_profit": previous_profit,
    }

# Test cases for Poker Sites
def test_add_poker_site_valid(client):
    response = client.post('/add_site', data={'site_name': 'Test Site', 'amount': '100.00', 'currency': 'USD'})
    assert response.status_code == 302 # Redirect

    # Verify data in DB
    with app.app_context():
        db = get_db()
        site = db.execute("SELECT * FROM sites WHERE name = 'Test Site'").fetchone()
        assert site is not None
        assert site['amount'] == 100.00
        assert site['currency'] == 'USD'

def test_bankroll_update_after_add_poker_site(client):
    bankroll_data_before = get_bankroll_data(client)
    client.post('/add_site', data={'site_name': 'Bankroll Test Site', 'amount': '75.00', 'currency': 'USD'})
    bankroll_data_after = get_bankroll_data(client)
    assert bankroll_data_after["current_poker_total"] == bankroll_data_before["current_poker_total"] + 75.00

def test_add_poker_site_invalid_amount(client):
    response = client.post('/add_site', data={'site_name': 'Invalid Site', 'amount': 'abc'})
    assert response.status_code == 400 # Bad Request

    with app.app_context():
        db = get_db()
        site = db.execute("SELECT * FROM sites WHERE name = 'Invalid Site'").fetchone()
        assert site is None # Should not be added

def test_add_poker_site_empty_name(client):
    response = client.post('/add_site', data={'site_name': '', 'amount': '100.00', 'currency': 'USD'})
    assert response.status_code == 400 # Bad Request

    with app.app_context():
        db = get_db()
        site = db.execute("SELECT * FROM sites WHERE name = ?", ('',)).fetchone()
        assert site is None # Should not be added

def test_update_poker_site_valid(client):
    # Add a site first
    client.post('/add_site', data={'site_name': 'Update Site', 'amount': '50.00', 'currency': 'USD'})
    with app.app_context():
        db = get_db()
        site_id = db.execute("SELECT id FROM sites WHERE name = 'Update Site'").fetchone()['id']

    response = client.post(f'/update_site/{site_id}', data={'site_name': 'Updated Site', 'amount': '150.00', 'currency': 'EUR'})
    assert response.status_code == 302

    with app.app_context():
        db = get_db()
        updated_site = db.execute("SELECT * FROM sites WHERE name = 'Updated Site' ORDER BY last_updated DESC").fetchone()
        assert updated_site is not None
        assert updated_site['amount'] == 150.00
        assert updated_site['currency'] == 'EUR'

def test_delete_poker_site(client):
    # Add a site first
    client.post('/add_site', data={'site_name': 'Delete Site', 'amount': '200.00', 'currency': 'USD'})
    with app.app_context():
        db = get_db()
        site_id = db.execute("SELECT id FROM sites WHERE name = 'Delete Site'").fetchone()['id']

    response = client.get(f'/perform_delete/site/{site_id}')
    assert response.status_code == 302

    with app.app_context():
        db = get_db()
        site = db.execute("SELECT * FROM sites WHERE id = ?", (site_id,)).fetchone()
        assert site is None

# Test cases for Assets (similar structure to Poker Sites)
def test_add_asset_valid(client):
    response = client.post('/add_asset', data={'name': 'Test Asset', 'amount': '500.00', 'currency': 'USD'})
    assert response.status_code == 302

    with app.app_context():
        db = get_db()
        asset = db.execute("SELECT * FROM assets WHERE name = 'Test Asset'").fetchone()
        assert asset is not None
        assert asset['amount'] == 500.00
        assert asset['currency'] == 'USD'

def test_update_asset_valid(client):
    client.post('/add_asset', data={'name': 'Update Asset', 'amount': '100.00', 'currency': 'USD'})
    with app.app_context():
        db = get_db()
        asset_id = db.execute("SELECT id FROM assets WHERE name = 'Update Asset'").fetchone()['id']

    response = client.post(f'/update_asset/{asset_id}', data={'name': 'Updated Asset', 'amount': '250.00', 'currency': 'EUR'})
    assert response.status_code == 302

    with app.app_context():
        db = get_db()
        updated_asset = db.execute("SELECT * FROM assets WHERE name = 'Updated Asset' ORDER BY last_updated DESC").fetchone()
        assert updated_asset is not None
        assert updated_asset['amount'] == 250.00
        assert updated_asset['currency'] == 'EUR'

def test_delete_asset(client):
    client.post('/add_asset', data={'name': 'Delete Asset', 'amount': '300.00', 'currency': 'USD'})
    with app.app_context():
        db = get_db()
        asset_id = db.execute("SELECT id FROM assets WHERE name = 'Delete Asset'").fetchone()['id']

    response = client.get(f'/perform_delete/asset/{asset_id}')
    assert response.status_code == 302

    with app.app_context():
        db = get_db()
        asset = db.execute("SELECT * FROM assets WHERE id = ?", (asset_id,)).fetchone()
        assert asset is None

# Test cases for Withdrawals
def test_add_withdrawal_valid(client):
    response = client.post('/add_withdrawal', data={'date': '2025-01-01', 'amount': '50.00', 'withdrawn_at': '1000.00'})
    assert response.status_code == 302 # Redirect

    with app.app_context():
        db = get_db()
        withdrawal = db.execute("SELECT * FROM drawings WHERE amount = 50.00").fetchone()
        assert withdrawal is not None
        assert withdrawal['date'] == '2025-01-01'
        assert withdrawal['withdrawn_at'] == 1000.00

def test_update_withdrawal_valid(client):
    client.post('/add_withdrawal', data={'date': '2025-01-01', 'amount': '50.00', 'withdrawn_at': '1000.00'})
    with app.app_context():
        db = get_db()
        withdrawal_id = db.execute("SELECT id FROM drawings WHERE amount = 50.00").fetchone()['id']

    response = client.post(f'/update_withdrawal/{withdrawal_id}', data={'date': '2025-01-02', 'amount': '75.00', 'withdrawn_at': '1200.00'})
    assert response.status_code == 302

    with app.app_context():
        db = get_db()
        updated_withdrawal = db.execute("SELECT * FROM drawings WHERE id = ?", (withdrawal_id,)).fetchone()
        assert updated_withdrawal is not None
        assert updated_withdrawal['amount'] == 75.00
        assert updated_withdrawal['date'] == '2025-01-02'

def test_delete_withdrawal(client):
    client.post('/add_withdrawal', data={'date': '2025-01-01', 'amount': '50.00', 'withdrawn_at': '1000.00'})
    with app.app_context():
        db = get_db()
        withdrawal_id = db.execute("SELECT id FROM drawings WHERE amount = 50.00").fetchone()['id']

    response = client.get(f'/perform_delete/withdrawal/{withdrawal_id}')
    assert response.status_code == 302

    with app.app_context():
        db = get_db()
        withdrawal = db.execute("SELECT * FROM drawings WHERE id = ?", (withdrawal_id,)).fetchone()
        assert withdrawal is None

# Test cases for Deposits
def test_add_deposit_valid(client):
    response = client.post('/add_deposit', data={'date': '2025-01-01', 'amount': '200.00', 'deposited_at': '500.00'})
    assert response.status_code == 302

    with app.app_context():
        db = get_db()
        deposit = db.execute("SELECT * FROM deposits WHERE amount = 200.00").fetchone()
        assert deposit is not None
        assert deposit['date'] == '2025-01-01'
        assert deposit['deposited_at'] == 500.00

def test_update_deposit_valid(client):
    client.post('/add_deposit', data={'date': '2025-01-01', 'amount': '200.00', 'deposited_at': '500.00'})
    with app.app_context():
        db = get_db()
        deposit_id = db.execute("SELECT id FROM deposits WHERE amount = 200.00").fetchone()['id']

    response = client.post(f'/update_deposit/{deposit_id}', data={'date': '2025-01-02', 'amount': '300.00', 'deposited_at': '600.00'})
    assert response.status_code == 302

    with app.app_context():
        db = get_db()
        updated_deposit = db.execute("SELECT * FROM deposits WHERE id = ?", (deposit_id,)).fetchone()
        assert updated_deposit is not None
        assert updated_deposit['amount'] == 300.00
        assert updated_deposit['date'] == '2025-01-02'

def test_delete_deposit(client):
    client.post('/add_deposit', data={'date': '2025-01-01', 'amount': '200.00', 'deposited_at': '500.00'})
    with app.app_context():
        db = get_db()
        deposit_id = db.execute("SELECT id FROM deposits WHERE amount = 200.00").fetchone()['id']

    response = client.get(f'/perform_delete/deposit/{deposit_id}')
    assert response.status_code == 302

    with app.app_context():
        db = get_db()
        deposit = db.execute("SELECT * FROM deposits WHERE id = ?", (deposit_id,)).fetchone()
        assert deposit is None