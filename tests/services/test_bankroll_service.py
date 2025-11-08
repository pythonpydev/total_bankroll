"""
Comprehensive tests for BankrollService.

Tests all 13 methods of the BankrollService class.
"""

import pytest
from decimal import Decimal
from datetime import datetime

from src.total_bankroll.services import BankrollService
from src.total_bankroll.models import Sites, Assets, Deposits, Drawings
from tests.factories import (
    UserFactory, SiteFactory, AssetFactory, 
    DepositFactory, DrawingFactory
)


class TestBankrollServiceCalculations:
    """Tests for bankroll calculation methods."""
    
    def test_calculate_total_bankroll_no_data(self, app, db, user):
        """Test calculating bankroll with no sites or assets."""
        with app.app_context():
            service = BankrollService()
            total = service.calculate_total_bankroll(user.id)
            
            assert total == Decimal('0.00')
    
    def test_calculate_total_bankroll_with_sites(self, app, db, user):
        """Test calculating bankroll with multiple sites."""
        with app.app_context():
            SiteFactory(user=user, balance=Decimal('1000.00'))
            SiteFactory(user=user, balance=Decimal('500.00'))
            db.session.commit()
            
            service = BankrollService()
            total = service.calculate_total_bankroll(user.id)
            
            assert total == Decimal('1500.00')
    
    def test_calculate_total_bankroll_with_assets(self, app, db, user):
        """Test calculating bankroll with assets."""
        with app.app_context():
            AssetFactory(user=user, value=Decimal('300.00'))
            AssetFactory(user=user, value=Decimal('200.00'))
            db.session.commit()
            
            service = BankrollService()
            total = service.calculate_total_bankroll(user.id)
            
            assert total == Decimal('500.00')
    
    def test_calculate_total_bankroll_sites_and_assets(self, app, db, user):
        """Test calculating bankroll with both sites and assets."""
        with app.app_context():
            SiteFactory(user=user, balance=Decimal('1000.00'))
            AssetFactory(user=user, value=Decimal('500.00'))
            db.session.commit()
            
            service = BankrollService()
            total = service.calculate_total_bankroll(user.id)
            
            assert total == Decimal('1500.00')
    
    def test_calculate_profit_no_transactions(self, app, db, user):
        """Test calculating profit with no deposits or drawings."""
        with app.app_context():
            service = BankrollService()
            profit = service.calculate_profit(user.id)
            
            assert profit == Decimal('0.00')
    
    def test_calculate_profit_with_deposits(self, app, db, user):
        """Test profit calculation with deposits only."""
        with app.app_context():
            DepositFactory(user=user, amount=Decimal('1000.00'))
            DepositFactory(user=user, amount=Decimal('500.00'))
            SiteFactory(user=user, balance=Decimal('2000.00'))
            db.session.commit()
            
            service = BankrollService()
            profit = service.calculate_profit(user.id)
            
            # Profit = Bankroll - Deposits + Drawings
            # = 2000 - 1500 + 0 = 500
            assert profit == Decimal('500.00')
    
    def test_calculate_profit_with_drawings(self, app, db, user):
        """Test profit calculation with deposits and withdrawals."""
        with app.app_context():
            DepositFactory(user=user, amount=Decimal('1000.00'))
            DrawingFactory(user=user, amount=Decimal('500.00'))
            SiteFactory(user=user, balance=Decimal('800.00'))
            db.session.commit()
            
            service = BankrollService()
            profit = service.calculate_profit(user.id)
            
            # Profit = Bankroll - Deposits + Drawings
            # = 800 - 1000 + 500 = 300
            assert profit == Decimal('300.00')
    
    def test_calculate_profit_with_loss(self, app, db, user):
        """Test profit calculation when user has lost money."""
        with app.app_context():
            DepositFactory(user=user, amount=Decimal('1000.00'))
            SiteFactory(user=user, balance=Decimal('600.00'))
            db.session.commit()
            
            service = BankrollService()
            profit = service.calculate_profit(user.id)
            
            # Lost 400
            assert profit == Decimal('-400.00')


class TestBankrollServiceSites:
    """Tests for site management methods."""
    
    def test_get_site_balances_empty(self, app, db, user):
        """Test getting site balances with no sites."""
        with app.app_context():
            service = BankrollService()
            balances = service.get_site_balances(user.id)
            
            assert balances == []
    
    def test_get_site_balances(self, app, db, user):
        """Test getting site balances."""
        with app.app_context():
            site1 = SiteFactory(user=user, site_name='PokerStars', balance=Decimal('1000.00'))
            site2 = SiteFactory(user=user, site_name='888poker', balance=Decimal('500.00'))
            db.session.commit()
            
            service = BankrollService()
            balances = service.get_site_balances(user.id)
            
            assert len(balances) == 2
            assert any(s.site_name == 'PokerStars' and s.balance == Decimal('1000.00') for s in balances)
            assert any(s.site_name == '888poker' and s.balance == Decimal('500.00') for s in balances)
    
    def test_add_site(self, app, db, user):
        """Test adding a new site."""
        with app.app_context():
            service = BankrollService()
            
            site_data = {
                'site_name': 'PartyPoker',
                'balance': Decimal('750.00'),
                'currency_id': 1
            }
            
            site = service.add_site(user.id, site_data)
            
            assert site is not None
            assert site.site_name == 'PartyPoker'
            assert site.balance == Decimal('750.00')
            assert site.user_id == user.id
    
    def test_update_site(self, app, db, user):
        """Test updating a site."""
        with app.app_context():
            site = SiteFactory(user=user, balance=Decimal('1000.00'))
            db.session.commit()
            
            service = BankrollService()
            
            updated = service.update_site(
                site.id,
                {'balance': Decimal('1500.00')}
            )
            
            assert updated is not None
            assert updated.balance == Decimal('1500.00')
    
    def test_update_site_not_found(self, app, db):
        """Test updating a non-existent site."""
        with app.app_context():
            service = BankrollService()
            
            result = service.update_site(99999, {'balance': Decimal('100.00')})
            
            assert result is None
    
    def test_delete_site(self, app, db, user):
        """Test deleting a site."""
        with app.app_context():
            site = SiteFactory(user=user)
            site_id = site.id
            db.session.commit()
            
            service = BankrollService()
            result = service.delete_site(site_id)
            
            assert result is True
            assert db.session.get(Sites, site_id) is None
    
    def test_delete_site_not_found(self, app, db):
        """Test deleting a non-existent site."""
        with app.app_context():
            service = BankrollService()
            result = service.delete_site(99999)
            
            assert result is False


class TestBankrollServiceAssets:
    """Tests for asset management methods."""
    
    def test_get_asset_values_empty(self, app, db, user):
        """Test getting asset values with no assets."""
        with app.app_context():
            service = BankrollService()
            values = service.get_asset_values(user.id)
            
            assert values == []
    
    def test_get_asset_values(self, app, db, user):
        """Test getting asset values."""
        with app.app_context():
            asset1 = AssetFactory(user=user, asset_name='Cash', value=Decimal('500.00'))
            asset2 = AssetFactory(user=user, asset_name='Crypto', value=Decimal('300.00'))
            db.session.commit()
            
            service = BankrollService()
            values = service.get_asset_values(user.id)
            
            assert len(values) == 2
            assert any(a.asset_name == 'Cash' and a.value == Decimal('500.00') for a in values)
            assert any(a.asset_name == 'Crypto' and a.value == Decimal('300.00') for a in values)
    
    def test_add_asset(self, app, db, user):
        """Test adding a new asset."""
        with app.app_context():
            service = BankrollService()
            
            asset_data = {
                'asset_name': 'Bank Account',
                'value': Decimal('2000.00'),
                'currency_id': 1
            }
            
            asset = service.add_asset(user.id, asset_data)
            
            assert asset is not None
            assert asset.asset_name == 'Bank Account'
            assert asset.value == Decimal('2000.00')
            assert asset.user_id == user.id
    
    def test_update_asset(self, app, db, user):
        """Test updating an asset."""
        with app.app_context():
            asset = AssetFactory(user=user, value=Decimal('500.00'))
            db.session.commit()
            
            service = BankrollService()
            
            updated = service.update_asset(
                asset.id,
                {'value': Decimal('750.00')}
            )
            
            assert updated is not None
            assert updated.value == Decimal('750.00')
    
    def test_update_asset_not_found(self, app, db):
        """Test updating a non-existent asset."""
        with app.app_context():
            service = BankrollService()
            
            result = service.update_asset(99999, {'value': Decimal('100.00')})
            
            assert result is None
    
    def test_delete_asset(self, app, db, user):
        """Test deleting an asset."""
        with app.app_context():
            asset = AssetFactory(user=user)
            asset_id = asset.id
            db.session.commit()
            
            service = BankrollService()
            result = service.delete_asset(asset_id)
            
            assert result is True
            assert db.session.get(Assets, asset_id) is None
    
    def test_delete_asset_not_found(self, app, db):
        """Test deleting a non-existent asset."""
        with app.app_context():
            service = BankrollService()
            result = service.delete_asset(99999)
            
            assert result is False


class TestBankrollServiceTransactions:
    """Tests for deposit/drawing methods."""
    
    def test_get_deposits_empty(self, app, db, user):
        """Test getting deposits with no transactions."""
        with app.app_context():
            service = BankrollService()
            deposits = service.get_deposits(user.id)
            
            assert deposits == []
    
    def test_get_deposits(self, app, db, user):
        """Test getting deposits."""
        with app.app_context():
            DepositFactory(user=user, amount=Decimal('1000.00'))
            DepositFactory(user=user, amount=Decimal('500.00'))
            db.session.commit()
            
            service = BankrollService()
            deposits = service.get_deposits(user.id)
            
            assert len(deposits) == 2
    
    def test_get_drawings_empty(self, app, db, user):
        """Test getting drawings with no transactions."""
        with app.app_context():
            service = BankrollService()
            drawings = service.get_drawings(user.id)
            
            assert drawings == []
    
    def test_get_drawings(self, app, db, user):
        """Test getting drawings."""
        with app.app_context():
            DrawingFactory(user=user, amount=Decimal('500.00'))
            DrawingFactory(user=user, amount=Decimal('250.00'))
            db.session.commit()
            
            service = BankrollService()
            drawings = service.get_drawings(user.id)
            
            assert len(drawings) == 2


class TestBankrollServiceBreakdown:
    """Tests for get_bankroll_breakdown method."""
    
    def test_get_bankroll_breakdown_complete(self, app, db, user):
        """Test getting complete bankroll breakdown."""
        with app.app_context():
            # Create sites
            SiteFactory(user=user, site_name='Site1', balance=Decimal('1000.00'))
            SiteFactory(user=user, site_name='Site2', balance=Decimal('500.00'))
            
            # Create assets
            AssetFactory(user=user, asset_name='Cash', value=Decimal('300.00'))
            
            # Create transactions
            DepositFactory(user=user, amount=Decimal('2000.00'))
            DrawingFactory(user=user, amount=Decimal('500.00'))
            
            db.session.commit()
            
            service = BankrollService()
            breakdown = service.get_bankroll_breakdown(user.id)
            
            assert breakdown['total_bankroll'] == Decimal('1800.00')
            assert breakdown['total_profit'] == Decimal('300.00')
            assert len(breakdown['sites']) == 2
            assert len(breakdown['assets']) == 1
            assert len(breakdown['deposits']) == 1
            assert len(breakdown['drawings']) == 1
    
    def test_get_bankroll_breakdown_empty(self, app, db, user):
        """Test getting breakdown with no data."""
        with app.app_context():
            service = BankrollService()
            breakdown = service.get_bankroll_breakdown(user.id)
            
            assert breakdown['total_bankroll'] == Decimal('0.00')
            assert breakdown['total_profit'] == Decimal('0.00')
            assert breakdown['sites'] == []
            assert breakdown['assets'] == []
            assert breakdown['deposits'] == []
            assert breakdown['drawings'] == []


class TestBankrollServiceErrorHandling:
    """Tests for error handling."""
    
    def test_calculate_total_bankroll_invalid_user(self, app, db):
        """Test calculating bankroll for non-existent user."""
        with app.app_context():
            service = BankrollService()
            total = service.calculate_total_bankroll(99999)
            
            assert total == Decimal('0.00')
    
    def test_add_site_missing_required_field(self, app, db, user):
        """Test adding site with missing required field."""
        with app.app_context():
            service = BankrollService()
            
            # Missing site_name
            site_data = {
                'balance': Decimal('100.00'),
                'currency_id': 1
            }
            
            with pytest.raises(Exception):
                service.add_site(user.id, site_data)
    
    def test_update_site_invalid_data(self, app, db, user):
        """Test updating site with invalid data."""
        with app.app_context():
            site = SiteFactory(user=user)
            db.session.commit()
            
            service = BankrollService()
            
            # Try to update with invalid balance
            with pytest.raises(Exception):
                service.update_site(site.id, {'balance': 'invalid'})
