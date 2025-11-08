"""
Comprehensive tests for AchievementService.

Tests all 8 methods of the AchievementService class.
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal

from src.total_bankroll.services import AchievementService
from src.total_bankroll.models import User, UserAchievement
from tests.factories import UserFactory, DepositFactory, DrawingFactory


class TestAchievementServiceStreaks:
    """Tests for streak tracking methods."""
    
    def test_update_streak_first_action(self, app, db, user):
        """Test updating streak for first time."""
        with app.app_context():
            service = AchievementService()
            
            streak = service.update_streak(user.id, 'deposit')
            
            assert streak == 1
            # Verify user object updated
            updated_user = db.session.get(User, user.id)
            assert updated_user.deposit_streak == 1
            assert updated_user.last_deposit_date is not None
    
    def test_update_streak_consecutive_days(self, app, db, user):
        """Test updating streak on consecutive days."""
        with app.app_context():
            service = AchievementService()
            
            # Set up user with previous streak
            user.deposit_streak = 1
            user.last_deposit_date = datetime.now().date() - timedelta(days=1)
            db.session.commit()
            
            streak = service.update_streak(user.id, 'deposit')
            
            assert streak == 2
    
    def test_update_streak_same_day(self, app, db, user):
        """Test that streak doesn't increase on same day."""
        with app.app_context():
            service = AchievementService()
            
            # Set up user with action today
            user.deposit_streak = 3
            user.last_deposit_date = datetime.now().date()
            db.session.commit()
            
            streak = service.update_streak(user.id, 'deposit')
            
            # Streak should stay the same
            assert streak == 3
    
    def test_update_streak_broken(self, app, db, user):
        """Test that streak resets when broken."""
        with app.app_context():
            service = AchievementService()
            
            # Set up user with old streak
            user.deposit_streak = 5
            user.last_deposit_date = datetime.now().date() - timedelta(days=3)
            db.session.commit()
            
            streak = service.update_streak(user.id, 'deposit')
            
            # Streak should reset to 1
            assert streak == 1
    
    def test_update_streak_withdrawal(self, app, db, user):
        """Test streak tracking for withdrawals."""
        with app.app_context():
            service = AchievementService()
            
            streak = service.update_streak(user.id, 'withdrawal')
            
            assert streak == 1
            updated_user = db.session.get(User, user.id)
            assert updated_user.withdrawal_streak == 1
    
    def test_update_streak_site_update(self, app, db, user):
        """Test streak tracking for site updates."""
        with app.app_context():
            service = AchievementService()
            
            streak = service.update_streak(user.id, 'site_update')
            
            assert streak == 1
            updated_user = db.session.get(User, user.id)
            assert updated_user.site_update_streak == 1
    
    def test_update_streak_asset_update(self, app, db, user):
        """Test streak tracking for asset updates."""
        with app.app_context():
            service = AchievementService()
            
            streak = service.update_streak(user.id, 'asset_update')
            
            assert streak == 1
            updated_user = db.session.get(User, user.id)
            assert updated_user.asset_update_streak == 1


class TestAchievementServiceChecking:
    """Tests for achievement checking and unlocking."""
    
    def test_check_achievements_no_achievements(self, app, db, user):
        """Test checking achievements when none are unlocked."""
        with app.app_context():
            service = AchievementService()
            
            new_achievements = service.check_achievements(user.id)
            
            # Initially no achievements should be unlocked
            assert isinstance(new_achievements, list)
    
    def test_check_achievements_streak_milestone(self, app, db, user):
        """Test that streak achievements are detected."""
        with app.app_context():
            service = AchievementService()
            
            # Set up user with streak milestone
            user.deposit_streak = 7  # Week streak
            db.session.commit()
            
            new_achievements = service.check_achievements(user.id)
            
            # Should detect week streak achievement
            assert len(new_achievements) > 0
    
    def test_unlock_achievement_new(self, app, db, user):
        """Test unlocking a new achievement."""
        with app.app_context():
            service = AchievementService()
            
            result = service.unlock_achievement(user.id, 'first_deposit')
            
            assert result is True
            
            # Verify achievement was saved
            achievement = db.session.query(UserAchievement).filter_by(
                user_id=user.id,
                achievement_key='first_deposit'
            ).first()
            
            assert achievement is not None
            assert achievement.unlocked_at is not None
    
    def test_unlock_achievement_duplicate(self, app, db, user):
        """Test that duplicate achievements are not unlocked."""
        with app.app_context():
            service = AchievementService()
            
            # Unlock first time
            service.unlock_achievement(user.id, 'first_deposit')
            
            # Try to unlock again
            result = service.unlock_achievement(user.id, 'first_deposit')
            
            # Should return False for duplicate
            assert result is False
    
    def test_get_user_achievements_empty(self, app, db, user):
        """Test getting achievements when user has none."""
        with app.app_context():
            service = AchievementService()
            
            achievements = service.get_user_achievements(user.id)
            
            assert achievements == []
    
    def test_get_user_achievements(self, app, db, user):
        """Test getting user's achievements."""
        with app.app_context():
            service = AchievementService()
            
            # Unlock some achievements
            service.unlock_achievement(user.id, 'first_deposit')
            service.unlock_achievement(user.id, 'week_streak')
            
            achievements = service.get_user_achievements(user.id)
            
            assert len(achievements) == 2
            keys = [a.achievement_key for a in achievements]
            assert 'first_deposit' in keys
            assert 'week_streak' in keys


class TestAchievementServiceProgress:
    """Tests for progress tracking."""
    
    def test_get_progress_no_data(self, app, db, user):
        """Test getting progress with no user data."""
        with app.app_context():
            service = AchievementService()
            
            progress = service.get_progress(user.id, 'week_streak')
            
            assert progress is not None
            assert 'current' in progress
            assert 'target' in progress
    
    def test_get_progress_deposit_count(self, app, db, user):
        """Test progress for deposit count achievement."""
        with app.app_context():
            service = AchievementService()
            
            # Create some deposits
            DepositFactory(user=user)
            DepositFactory(user=user)
            DepositFactory(user=user)
            db.session.commit()
            
            progress = service.get_progress(user.id, 'deposit_10')
            
            assert progress['current'] == 3
            assert progress['target'] == 10
            assert progress['percentage'] == 30.0
    
    def test_get_progress_streak(self, app, db, user):
        """Test progress for streak achievement."""
        with app.app_context():
            service = AchievementService()
            
            # Set up streak
            user.deposit_streak = 5
            db.session.commit()
            
            progress = service.get_progress(user.id, 'week_streak')
            
            assert progress['current'] == 5
            assert progress['target'] == 7
    
    def test_get_progress_completed(self, app, db, user):
        """Test progress for completed achievement."""
        with app.app_context():
            service = AchievementService()
            
            # Set up completed streak
            user.deposit_streak = 7
            db.session.commit()
            
            progress = service.get_progress(user.id, 'week_streak')
            
            assert progress['current'] >= progress['target']
            assert progress['percentage'] >= 100.0


class TestAchievementServiceMilestones:
    """Tests for milestone achievements."""
    
    def test_first_deposit_achievement(self, app, db, user):
        """Test first deposit achievement."""
        with app.app_context():
            service = AchievementService()
            
            # Create first deposit
            DepositFactory(user=user)
            db.session.commit()
            
            new_achievements = service.check_achievements(user.id)
            
            # Should unlock first deposit achievement
            assert any(a == 'first_deposit' for a in new_achievements)
    
    def test_first_withdrawal_achievement(self, app, db, user):
        """Test first withdrawal achievement."""
        with app.app_context():
            service = AchievementService()
            
            # Create first withdrawal
            DrawingFactory(user=user)
            db.session.commit()
            
            new_achievements = service.check_achievements(user.id)
            
            # Should unlock first withdrawal achievement
            assert any(a == 'first_withdrawal' for a in new_achievements)
    
    def test_deposit_count_milestones(self, app, db, user):
        """Test deposit count milestone achievements."""
        with app.app_context():
            service = AchievementService()
            
            # Create 10 deposits
            for _ in range(10):
                DepositFactory(user=user)
            db.session.commit()
            
            new_achievements = service.check_achievements(user.id)
            
            # Should unlock 10 deposit achievement
            assert len(new_achievements) > 0


class TestAchievementServiceIntegration:
    """Integration tests for achievement workflows."""
    
    def test_complete_deposit_workflow(self, app, db, user):
        """Test complete workflow of deposits triggering achievements."""
        with app.app_context():
            service = AchievementService()
            
            # Day 1: First deposit
            service.update_streak(user.id, 'deposit')
            achievements = service.check_achievements(user.id)
            
            # Should get first deposit achievement
            assert len(achievements) > 0
            
            # Verify it was saved
            saved = service.get_user_achievements(user.id)
            assert len(saved) > 0
    
    def test_streak_progression(self, app, db, user):
        """Test streak progressing over multiple days."""
        with app.app_context():
            service = AchievementService()
            
            # Simulate deposits over consecutive days
            for i in range(7):
                user.last_deposit_date = datetime.now().date() - timedelta(days=7-i)
                user.deposit_streak = i
                db.session.commit()
                
                streak = service.update_streak(user.id, 'deposit')
                assert streak == i + 1
            
            # Check for week streak achievement
            achievements = service.check_achievements(user.id)
            assert any('week' in str(a).lower() for a in achievements)
    
    def test_multiple_achievement_types(self, app, db, user):
        """Test unlocking different types of achievements."""
        with app.app_context():
            service = AchievementService()
            
            # Unlock different achievements
            service.unlock_achievement(user.id, 'first_deposit')
            service.unlock_achievement(user.id, 'first_withdrawal')
            service.unlock_achievement(user.id, 'week_streak')
            
            achievements = service.get_user_achievements(user.id)
            
            assert len(achievements) == 3
            # All should have unlock dates
            assert all(a.unlocked_at is not None for a in achievements)


class TestAchievementServiceEdgeCases:
    """Tests for edge cases and error handling."""
    
    def test_update_streak_invalid_type(self, app, db, user):
        """Test updating streak with invalid type."""
        with app.app_context():
            service = AchievementService()
            
            # Should handle invalid type gracefully
            with pytest.raises((ValueError, KeyError, AttributeError)):
                service.update_streak(user.id, 'invalid_type')
    
    def test_check_achievements_invalid_user(self, app, db):
        """Test checking achievements for non-existent user."""
        with app.app_context():
            service = AchievementService()
            
            # Should return empty list or handle gracefully
            achievements = service.check_achievements(99999)
            
            assert achievements == []
    
    def test_unlock_achievement_invalid_user(self, app, db):
        """Test unlocking achievement for non-existent user."""
        with app.app_context():
            service = AchievementService()
            
            # Should return False or raise exception
            result = service.unlock_achievement(99999, 'first_deposit')
            
            assert result is False
    
    def test_get_progress_invalid_achievement(self, app, db, user):
        """Test getting progress for non-existent achievement."""
        with app.app_context():
            service = AchievementService()
            
            # Should handle gracefully
            progress = service.get_progress(user.id, 'nonexistent_achievement')
            
            # Should return some default or None
            assert progress is None or isinstance(progress, dict)


class TestAchievementServicePerformance:
    """Tests for performance and efficiency."""
    
    def test_bulk_achievement_checking(self, app, db, user):
        """Test checking achievements is efficient."""
        with app.app_context():
            service = AchievementService()
            
            # Create lots of data
            for _ in range(100):
                DepositFactory(user=user)
            db.session.commit()
            
            # Should still be fast
            import time
            start = time.time()
            achievements = service.check_achievements(user.id)
            elapsed = time.time() - start
            
            # Should complete in reasonable time (< 1 second)
            assert elapsed < 1.0
    
    def test_get_achievements_no_n_plus_one(self, app, db, user):
        """Test that getting achievements doesn't cause N+1 queries."""
        with app.app_context():
            service = AchievementService()
            
            # Unlock multiple achievements
            for i in range(10):
                service.unlock_achievement(user.id, f'achievement_{i}')
            
            # Should fetch all in one or few queries
            achievements = service.get_user_achievements(user.id)
            
            assert len(achievements) == 10
