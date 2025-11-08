"""
Comprehensive tests for RecommendationService.

Tests all 5 methods of the RecommendationService class.
"""

import pytest
from decimal import Decimal
import json

from src.total_bankroll.services import RecommendationService
from tests.factories import UserFactory


class TestRecommendationServiceTournament:
    """Tests for tournament recommendation methods."""
    
    def test_get_tournament_recommendation_low_bankroll(self, app, db):
        """Test tournament recommendation with very low bankroll."""
        with app.app_context():
            service = RecommendationService()
            
            result = service.get_tournament_recommendation(
                total_bankroll=Decimal('50.00'),
                game_type='MTT',
                skill_level='Beginner',
                risk_tolerance='Conservative'
            )
            
            assert result is not None
            assert result['recommended_stake'] is not None
            # Should recommend micro stakes for low bankroll
            assert result['recommended_stake']['buy_in'] <= Decimal('2.00')
    
    def test_get_tournament_recommendation_high_bankroll(self, app, db):
        """Test tournament recommendation with high bankroll."""
        with app.app_context():
            service = RecommendationService()
            
            result = service.get_tournament_recommendation(
                total_bankroll=Decimal('50000.00'),
                game_type='MTT',
                skill_level='Advanced',
                risk_tolerance='Aggressive'
            )
            
            assert result is not None
            assert result['recommended_stake'] is not None
            # Should recommend higher stakes for large bankroll
            assert result['recommended_stake']['buy_in'] > Decimal('50.00')
    
    def test_get_tournament_recommendation_conservative(self, app, db):
        """Test conservative tournament recommendation."""
        with app.app_context():
            service = RecommendationService()
            
            conservative = service.get_tournament_recommendation(
                total_bankroll=Decimal('10000.00'),
                game_type='MTT',
                skill_level='Intermediate',
                risk_tolerance='Conservative'
            )
            
            aggressive = service.get_tournament_recommendation(
                total_bankroll=Decimal('10000.00'),
                game_type='MTT',
                skill_level='Intermediate',
                risk_tolerance='Aggressive'
            )
            
            # Conservative should recommend lower stakes than aggressive
            assert conservative['recommended_stake']['buy_in'] <= \
                   aggressive['recommended_stake']['buy_in']
    
    def test_get_tournament_recommendation_move_up_threshold(self, app, db):
        """Test that move up threshold is calculated."""
        with app.app_context():
            service = RecommendationService()
            
            result = service.get_tournament_recommendation(
                total_bankroll=Decimal('1000.00'),
                game_type='MTT',
                skill_level='Intermediate',
                risk_tolerance='Moderate'
            )
            
            assert 'move_up_message' in result
            assert 'move_down_message' in result
    
    def test_get_tournament_recommendation_below_minimum(self, app, db):
        """Test recommendation when below minimum stake."""
        with app.app_context():
            service = RecommendationService()
            
            result = service.get_tournament_recommendation(
                total_bankroll=Decimal('10.00'),
                game_type='MTT',
                skill_level='Beginner',
                risk_tolerance='Conservative'
            )
            
            assert result is not None
            # Should still provide recommendation or guidance
            assert 'recommended_stake' in result or 'message' in result


class TestRecommendationServiceCashGame:
    """Tests for cash game recommendation methods."""
    
    def test_get_cash_game_recommendation_low_bankroll(self, app, db):
        """Test cash game recommendation with low bankroll."""
        with app.app_context():
            service = RecommendationService()
            
            result = service.get_cash_game_recommendation(
                total_bankroll=Decimal('100.00'),
                game_type='NLHE',
                skill_level='Beginner',
                risk_tolerance='Conservative'
            )
            
            assert result is not None
            assert result['recommended_stake'] is not None
            # Should recommend micro stakes
            assert result['recommended_stake']['big_blind'] <= Decimal('0.10')
    
    def test_get_cash_game_recommendation_high_bankroll(self, app, db):
        """Test cash game recommendation with high bankroll."""
        with app.app_context():
            service = RecommendationService()
            
            result = service.get_cash_game_recommendation(
                total_bankroll=Decimal('50000.00'),
                game_type='PLO',
                skill_level='Advanced',
                risk_tolerance='Aggressive'
            )
            
            assert result is not None
            assert result['recommended_stake'] is not None
            # Should recommend higher stakes
            assert result['recommended_stake']['big_blind'] > Decimal('1.00')
    
    def test_get_cash_game_recommendation_risk_comparison(self, app, db):
        """Test that risk tolerance affects recommendations."""
        with app.app_context():
            service = RecommendationService()
            
            conservative = service.get_cash_game_recommendation(
                total_bankroll=Decimal('5000.00'),
                game_type='NLHE',
                skill_level='Intermediate',
                risk_tolerance='Conservative'
            )
            
            aggressive = service.get_cash_game_recommendation(
                total_bankroll=Decimal('5000.00'),
                game_type='NLHE',
                skill_level='Intermediate',
                risk_tolerance='Aggressive'
            )
            
            # Conservative should recommend lower or equal stakes
            conservative_bb = conservative['recommended_stake']['big_blind']
            aggressive_bb = aggressive['recommended_stake']['big_blind']
            
            assert conservative_bb <= aggressive_bb
    
    def test_get_cash_game_recommendation_stop_loss(self, app, db):
        """Test that stop loss threshold is provided."""
        with app.app_context():
            service = RecommendationService()
            
            result = service.get_cash_game_recommendation(
                total_bankroll=Decimal('2000.00'),
                game_type='NLHE',
                skill_level='Intermediate',
                risk_tolerance='Moderate'
            )
            
            assert 'move_down_message' in result
            # Should indicate when to move down stakes
            assert 'move_up_message' in result


class TestRecommendationServiceWeightedRange:
    """Tests for _calculate_weighted_range method."""
    
    def test_calculate_weighted_range_tournament(self, app, db):
        """Test weighted range calculation for tournaments."""
        with app.app_context():
            service = RecommendationService()
            
            # This is a private method, but we can test it indirectly
            # through the public methods
            result = service.get_tournament_recommendation(
                total_bankroll=Decimal('5000.00'),
                game_type='MTT',
                skill_level='Intermediate',
                risk_tolerance='Moderate'
            )
            
            # Should provide reasonable recommendation
            assert result is not None
            assert result['recommended_stake']['buy_in'] > Decimal('0')
    
    def test_calculate_weighted_range_cash_game(self, app, db):
        """Test weighted range calculation for cash games."""
        with app.app_context():
            service = RecommendationService()
            
            result = service.get_cash_game_recommendation(
                total_bankroll=Decimal('5000.00'),
                game_type='NLHE',
                skill_level='Intermediate',
                risk_tolerance='Moderate'
            )
            
            # Should provide reasonable recommendation
            assert result is not None
            assert result['recommended_stake']['big_blind'] > Decimal('0')


class TestRecommendationServiceStakeSelection:
    """Tests for stake selection logic."""
    
    def test_tournament_stake_selection_exact_match(self, app, db):
        """Test when bankroll exactly matches a stake requirement."""
        with app.app_context():
            service = RecommendationService()
            
            # Find a bankroll that should match a specific stake
            result = service.get_tournament_recommendation(
                total_bankroll=Decimal('1100.00'),  # 100 * 11
                game_type='MTT',
                skill_level='Intermediate',
                risk_tolerance='Aggressive'  # Lower buy-in multiple
            )
            
            assert result is not None
            assert result['recommended_stake'] is not None
    
    def test_cash_game_stake_selection_highest_possible(self, app, db):
        """Test that highest playable stake is selected."""
        with app.app_context():
            service = RecommendationService()
            
            # Large bankroll should get high stakes recommendation
            result = service.get_cash_game_recommendation(
                total_bankroll=Decimal('100000.00'),
                game_type='NLHE',
                skill_level='Advanced',
                risk_tolerance='Aggressive'
            )
            
            assert result is not None
            # Should recommend one of the higher stakes
            assert result['recommended_stake']['big_blind'] >= Decimal('5.00')


class TestRecommendationServiceEdgeCases:
    """Tests for edge cases and error handling."""
    
    def test_zero_bankroll_tournament(self, app, db):
        """Test recommendation with zero bankroll."""
        with app.app_context():
            service = RecommendationService()
            
            result = service.get_tournament_recommendation(
                total_bankroll=Decimal('0.00'),
                game_type='MTT',
                skill_level='Beginner',
                risk_tolerance='Conservative'
            )
            
            assert result is not None
            # Should provide guidance even with zero bankroll
    
    def test_zero_bankroll_cash_game(self, app, db):
        """Test cash game recommendation with zero bankroll."""
        with app.app_context():
            service = RecommendationService()
            
            result = service.get_cash_game_recommendation(
                total_bankroll=Decimal('0.00'),
                game_type='NLHE',
                skill_level='Beginner',
                risk_tolerance='Conservative'
            )
            
            assert result is not None
    
    def test_invalid_game_type(self, app, db):
        """Test with invalid game type."""
        with app.app_context():
            service = RecommendationService()
            
            # Should handle gracefully or raise appropriate exception
            try:
                result = service.get_tournament_recommendation(
                    total_bankroll=Decimal('1000.00'),
                    game_type='INVALID',
                    skill_level='Intermediate',
                    risk_tolerance='Moderate'
                )
                # If it doesn't raise, it should return a result
                assert result is not None
            except (ValueError, KeyError):
                # Or it might raise an exception, which is also valid
                pass
    
    def test_negative_bankroll(self, app, db):
        """Test with negative bankroll."""
        with app.app_context():
            service = RecommendationService()
            
            # Should handle negative bankroll gracefully
            result = service.get_tournament_recommendation(
                total_bankroll=Decimal('-100.00'),
                game_type='MTT',
                skill_level='Beginner',
                risk_tolerance='Conservative'
            )
            
            assert result is not None


class TestRecommendationServiceDataLoading:
    """Tests for recommendation data loading."""
    
    def test_recommendation_logic_file_exists(self, app, db):
        """Test that recommendation logic JSON file is loaded."""
        with app.app_context():
            service = RecommendationService()
            
            # Service should have loaded the recommendation logic
            assert hasattr(service, 'recommendation_logic')
            assert service.recommendation_logic is not None
    
    def test_tournament_stakes_loaded(self, app, db):
        """Test that tournament stakes are loaded."""
        with app.app_context():
            service = RecommendationService()
            
            # Should have tournament stakes data
            assert hasattr(service, 'tournament_stakes')
            assert len(service.tournament_stakes) > 0
    
    def test_cash_stakes_loaded(self, app, db):
        """Test that cash game stakes are loaded."""
        with app.app_context():
            service = RecommendationService()
            
            # Should have cash stakes data
            assert hasattr(service, 'cash_stakes')
            assert len(service.cash_stakes) > 0


class TestRecommendationServiceConsistency:
    """Tests for recommendation consistency."""
    
    def test_same_inputs_same_output(self, app, db):
        """Test that same inputs produce same recommendations."""
        with app.app_context():
            service = RecommendationService()
            
            result1 = service.get_tournament_recommendation(
                total_bankroll=Decimal('5000.00'),
                game_type='MTT',
                skill_level='Intermediate',
                risk_tolerance='Moderate'
            )
            
            result2 = service.get_tournament_recommendation(
                total_bankroll=Decimal('5000.00'),
                game_type='MTT',
                skill_level='Intermediate',
                risk_tolerance='Moderate'
            )
            
            assert result1 == result2
    
    def test_increasing_bankroll_increases_stakes(self, app, db):
        """Test that larger bankroll recommends higher stakes."""
        with app.app_context():
            service = RecommendationService()
            
            small = service.get_cash_game_recommendation(
                total_bankroll=Decimal('500.00'),
                game_type='NLHE',
                skill_level='Intermediate',
                risk_tolerance='Moderate'
            )
            
            large = service.get_cash_game_recommendation(
                total_bankroll=Decimal('50000.00'),
                game_type='NLHE',
                skill_level='Intermediate',
                risk_tolerance='Moderate'
            )
            
            assert small['recommended_stake']['big_blind'] < \
                   large['recommended_stake']['big_blind']
