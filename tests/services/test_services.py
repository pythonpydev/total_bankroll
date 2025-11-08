"""
Unit tests for the Service Layer Base Class

Tests the common functionality provided by BaseService.
"""

import pytest
from decimal import Decimal
from total_bankroll.services.base import BaseService
from total_bankroll.models import db


class TestService(BaseService):
    """Test service for testing base functionality."""
    
    def test_method(self):
        """Simple test method."""
        return "test"


class TestBaseService:
    """Test cases for BaseService."""
    
    def test_service_initialization(self, app):
        """Test that service initializes correctly."""
        with app.app_context():
            service = TestService()
            assert service.db is not None
            assert service.db == db
    
    def test_logging_methods(self, app):
        """Test that logging methods work without errors."""
        with app.app_context():
            service = TestService()
            
            # These should not raise exceptions
            service._log_info("Test info message")
            service._log_error("Test error message")
            service._log_debug("Test debug message")
    
    def test_database_operations(self, app):
        """Test basic database operation wrappers."""
        with app.app_context():
            service = TestService()
            
            # Test rollback doesn't raise error
            service.rollback()
            
            # Test flush doesn't raise error
            service.flush()
    
    def test_commit_on_empty_session(self, app):
        """Test commit with no changes."""
        with app.app_context():
            service = TestService()
            result = service.commit()
            assert result == True
    
    def test_service_has_logger(self, app):
        """Test that service has access to logger."""
        with app.app_context():
            service = TestService()
            assert service.logger is not None


class TestBankrollService:
    """Test cases for BankrollService."""
    
    def test_bankroll_service_imports(self):
        """Test that BankrollService can be imported."""
        from total_bankroll.services import BankrollService
        assert BankrollService is not None
    
    def test_bankroll_service_initialization(self, app):
        """Test that BankrollService initializes."""
        from total_bankroll.services import BankrollService
        
        with app.app_context():
            service = BankrollService()
            assert service is not None
            assert hasattr(service, 'calculate_total_bankroll')
            assert hasattr(service, 'get_site_balances')
    
    def test_calculate_total_bankroll_returns_decimal(self, app):
        """Test that calculate_total_bankroll returns a Decimal."""
        from total_bankroll.services import BankrollService
        
        with app.app_context():
            service = BankrollService()
            result = service.calculate_total_bankroll(user_id=1)
            assert isinstance(result, Decimal)


class TestCurrencyService:
    """Test cases for CurrencyService."""
    
    def test_currency_service_imports(self):
        """Test that CurrencyService can be imported."""
        from total_bankroll.services import CurrencyService
        assert CurrencyService is not None
    
    def test_currency_service_initialization(self, app):
        """Test that CurrencyService initializes."""
        from total_bankroll.services import CurrencyService
        
        with app.app_context():
            service = CurrencyService()
            assert service is not None
            assert hasattr(service, 'convert')
            assert hasattr(service, 'get_exchange_rate')
    
    def test_convert_same_currency(self, app):
        """Test converting between same currency returns same amount."""
        from total_bankroll.services import CurrencyService
        
        with app.app_context():
            service = CurrencyService()
            amount = Decimal('100.00')
            result = service.convert(amount, 'USD', 'USD')
            assert result == amount


class TestRecommendationService:
    """Test cases for RecommendationService."""
    
    def test_recommendation_service_imports(self):
        """Test that RecommendationService can be imported."""
        from total_bankroll.services import RecommendationService
        assert RecommendationService is not None
    
    def test_recommendation_service_initialization(self, app):
        """Test that RecommendationService initializes."""
        from total_bankroll.services import RecommendationService
        
        with app.app_context():
            service = RecommendationService()
            assert service is not None
            assert hasattr(service, 'get_cash_game_recommendation')
            assert hasattr(service, 'get_tournament_recommendation')


class TestAchievementService:
    """Test cases for AchievementService."""
    
    def test_achievement_service_imports(self):
        """Test that AchievementService can be imported."""
        from total_bankroll.services import AchievementService
        assert AchievementService is not None
    
    def test_achievement_service_initialization(self, app):
        """Test that AchievementService initializes."""
        from total_bankroll.services import AchievementService
        
        with app.app_context():
            service = AchievementService()
            assert service is not None
            assert hasattr(service, 'check_achievements')
            assert hasattr(service, 'update_streak')
