import pytest
from flask import url_for
from total_bankroll.models import Sites, SiteHistory, Assets, AssetHistory, Drawings, Deposits
from decimal import Decimal

# Test cases for Poker Sites
def test_add_poker_site_valid(client, new_user, db):
    with client:
        client.post(url_for('auth.login'), data={'email': new_user.email, 'password': 'password123'}, follow_redirects=True)
        response = client.post(url_for('poker_sites.add_site'), data={
            'name': 'Test Site',
            'amount': '100.00',
            'currency': 'USD',
            'submit': 'Add Site'
        })
        # The modal form submission returns a redirect on success
        assert response.status_code == 302

        # Verify data in DB
        site = db.session.query(Sites).filter_by(name='Test Site', user_id=new_user.id).first()
        assert site is not None
        history = db.session.query(SiteHistory).filter_by(site_id=site.id).first()
        assert history is not None
        assert history.amount == Decimal('100.00')
        assert history.currency == 'USD'

def test_add_poker_site_invalid_amount(client, new_user, db):
    with client:
        client.post(url_for('auth.login'), data={'email': new_user.email, 'password': 'password123'}, follow_redirects=True)
        response = client.post(url_for('poker_sites.add_site'), data={
            'name': 'Invalid Site',
            'amount': 'abc',
            'currency': 'USD',
            'submit': 'Add Site'
        })
        assert response.status_code == 400 # Expect a bad request on validation error
        json_data = response.get_json()
        assert 'This field is required.' in json_data['errors']['amount']

        site = db.session.query(Sites).filter_by(name='Invalid Site').first()
        assert site is None # Should not be added

def test_add_poker_site_empty_name(client, new_user, db):
    with client:
        client.post(url_for('auth.login'), data={'email': new_user.email, 'password': 'password123'}, follow_redirects=True)
        response = client.post(url_for('poker_sites.add_site'), data={
            'name': '',
            'amount': '100.00',
            'currency': 'USD',
            'submit': 'Add Site'
        })
        assert response.status_code == 400 # Expect a bad request on validation error
        json_data = response.get_json()
        assert 'This field is required.' in json_data['errors']['name']

        site = db.session.query(Sites).filter_by(name='').first()
        assert site is None # Should not be added

def test_update_poker_site_valid(client, new_user, db):
    with client:
        client.post(url_for('auth.login'), data={'email': new_user.email, 'password': 'password123'}, follow_redirects=True)
        # Add a site directly to the DB for a more robust test setup
        site = Sites(name='Update Site', user_id=new_user.id)
        db.session.add(site)
        db.session.commit()

        response = client.post(url_for('poker_sites.update_site', site_id=site.id), data={'amount': '150.00', 'submit': 'Update Amount'}, follow_redirects=True)
        assert response.status_code == 200

        history_records = db.session.query(SiteHistory).filter_by(site_id=site.id).order_by(SiteHistory.recorded_at.desc()).all()
        assert len(history_records) == 1
        assert history_records[0].amount == Decimal('150.00')

def test_delete_poker_site(client, new_user, db):
    with client:
        client.post(url_for('auth.login'), data={'email': new_user.email, 'password': 'password123'}, follow_redirects=True)
        # Add a site directly to the DB
        site = Sites(name='Delete Site', user_id=new_user.id)
        db.session.add(site)
        db.session.commit()

        response = client.post(url_for('common.perform_delete', item_type='site', item_id=site.id), follow_redirects=True)
        assert response.status_code == 200

        deleted_site = db.session.query(Sites).filter_by(id=site.id).first()
        assert deleted_site is None

# Test cases for Assets (similar structure to Poker Sites)
def test_add_asset_valid(client, new_user, db):
    with client:
        client.post(url_for('auth.login'), data={'email': new_user.email, 'password': 'password123'}, follow_redirects=True)
        response = client.post(url_for('assets.add_asset'), data={
            'name': 'Test Asset',
            'amount': '500.00',
            'currency': 'USD',
            'submit': 'Add Asset'
        })
        assert response.status_code == 302 # Redirect on success

        asset = db.session.query(Assets).filter_by(name='Test Asset', user_id=new_user.id).first()
        assert asset is not None
        history = db.session.query(AssetHistory).filter_by(asset_id=asset.id).first()
        assert history.amount == Decimal('500.00')

# Test cases for Withdrawals
def test_add_withdrawal_valid(client, new_user, db):
    with client:
        client.post(url_for('auth.login'), data={'email': new_user.email, 'password': 'password123'}, follow_redirects=True)
        response = client.post(url_for('add_withdrawal.add_withdrawal'), data={'date': '2025-01-01', 'amount': '50.00', 'currency': 'USD'})
        assert response.status_code == 302

        withdrawal = db.session.query(Drawings).filter_by(amount=Decimal('50.00'), user_id=new_user.id).first()
        assert withdrawal is not None
        assert withdrawal.date.strftime('%Y-%m-%d') == '2025-01-01'

# Test cases for Deposits
def test_add_deposit_valid(client, new_user, db):
    with client:
        client.post(url_for('auth.login'), data={'email': new_user.email, 'password': 'password123'}, follow_redirects=True)
        response = client.post(url_for('add_deposit.add_deposit'), data={'date': '2025-01-01', 'amount': '200.00', 'currency': 'USD'})
        assert response.status_code == 302

        deposit = db.session.query(Deposits).filter_by(amount=Decimal('200.00'), user_id=new_user.id).first()
        assert deposit is not None
        assert deposit.date.strftime('%Y-%m-%d') == '2025-01-01'