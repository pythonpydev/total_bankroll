"""
Achievement Service

Handles all achievement-related business logic including:
- Achievement checking and unlocking
- Streak tracking
- Progress monitoring
- User achievement history

This service manages the gamification features of the application.
"""

from typing import Dict, Any, List, Optional
from datetime import date, timedelta
from flask import flash
from .base import BaseService
from ..models import db, User, Achievement, UserAchievement


# Define all achievements in a central dictionary for easy management.
ACHIEVEMENT_DEFINITIONS = {
    'STREAK_3_DAY': {
        'name': 'Daily Tracker',
        'description': 'Logged an update for 3 consecutive days.',
        'category': 'Consistency',
        'icon': 'bi-calendar-check',
        'target': 3
    },
    'STREAK_7_DAY': {
        'name': 'Weekly Warrior',
        'description': 'Logged an update for 7 consecutive days.',
        'category': 'Consistency',
        'icon': 'bi-calendar-week',
        'target': 7
    },
    'STREAK_30_DAY': {
        'name': 'Grinder\'s Routine',
        'description': 'Logged an update for 30 consecutive days.',
        'category': 'Consistency',
        'icon': 'bi-calendar-range',
        'target': 30
    },
    'GOAL_CRUSHER': {
        'name': 'Goal Crusher',
        'description': 'Successfully completed your first goal.',
        'category': 'Milestone',
        'icon': 'bi-trophy'
    },
    'READ_1_ARTICLE': {
        'name': 'Bookworm',
        'description': 'Read your first strategy article.',
        'category': 'Study',
        'icon': 'bi-book'
    },
    'READ_10_ARTICLES': {
        'name': 'PLO Scholar',
        'description': 'Read 10 different PLO articles.',
        'category': 'Study',
        'icon': 'bi-mortarboard',
        'target': 10
    },
    'THE_TECHNICIAN': {
        'name': 'The Technician',
        'description': 'Used one of the poker tools for the first time.',
        'category': 'Study',
        'icon': 'bi-tools'
    },
    'BANKROLL_1K': {
        'name': '$1K Club',
        'description': 'Reached a bankroll of $1,000.',
        'category': 'Milestone',
        'icon': 'bi-cash-stack',
        'target': 1000
    },
    'BANKROLL_10K': {
        'name': '$10K Club',
        'description': 'Reached a bankroll of $10,000.',
        'category': 'Milestone',
        'icon': 'bi-gem',
        'target': 10000
    },
}


class AchievementService(BaseService):
    """
    Service for managing achievements and gamification.
    
    Tracks user progress, awards achievements, and manages streaks.
    """
    
    def __init__(self):
        """Initialize the AchievementService."""
        super().__init__()
    
    def check_achievements(self, user: User, bankroll_data: Optional[Dict[str, Any]] = None) -> List[str]:
        """
        Check all achievement conditions for a user and award them if met.
        
        Args:
            user: The User object to check achievements for
            bankroll_data: Optional pre-fetched bankroll data (to avoid redundant queries)
        
        Returns:
            List of achievement keys that were newly unlocked
        
        Example:
            >>> service = AchievementService()
            >>> user = User.query.get(1)
            >>> unlocked = service.check_achievements(user)
            >>> print(f"Unlocked: {unlocked}")
        """
        self._log_debug(f"Checking achievements for user {user.id}")
        
        # Get achievements the user has already unlocked to avoid re-awarding
        unlocked_keys = {ua.achievement.key for ua in user.user_achievements}
        newly_unlocked = []
        
        # Get bankroll data if not provided
        if bankroll_data is None:
            from ..services import BankrollService
            bankroll_service = BankrollService()
            bankroll_data = bankroll_service.get_bankroll_breakdown(user.id)
        
        # --- 1. Check Streak Achievements ---
        streak_achievements = {
            'STREAK_3_DAY': 3,
            'STREAK_7_DAY': 7,
            'STREAK_30_DAY': 30
        }
        for key, required_streak in streak_achievements.items():
            if user.streak_days >= required_streak and key not in unlocked_keys:
                if self._unlock_achievement(user.id, key):
                    newly_unlocked.append(key)
        
        # --- 2. Check Bankroll Milestones ---
        bankroll_milestones = {
            'BANKROLL_1K': 1000,
            'BANKROLL_10K': 10000
        }
        total_bankroll = bankroll_data.get('total_bankroll', 0.0)
        
        for key, required_amount in bankroll_milestones.items():
            if total_bankroll >= required_amount and key not in unlocked_keys:
                if self._unlock_achievement(user.id, key):
                    newly_unlocked.append(key)
        
        # --- 3. Check Goal Achievements ---
        completed_goal_count = user.goals.filter_by(status='completed').count()
        if completed_goal_count > 0 and 'GOAL_CRUSHER' not in unlocked_keys:
            if self._unlock_achievement(user.id, 'GOAL_CRUSHER'):
                newly_unlocked.append('GOAL_CRUSHER')
        
        # --- 4. Check Article Reading Achievements ---
        read_count = len(user.read_articles)
        article_achievements = {
            'READ_1_ARTICLE': 1,
            'READ_10_ARTICLES': 10
        }
        for key, required_reads in article_achievements.items():
            if read_count >= required_reads and key not in unlocked_keys:
                if self._unlock_achievement(user.id, key):
                    newly_unlocked.append(key)
        
        # --- 5. Check Tool Usage Achievements ---
        tool_usage_count = len(user.tool_usages)
        if tool_usage_count > 0 and 'THE_TECHNICIAN' not in unlocked_keys:
            if self._unlock_achievement(user.id, 'THE_TECHNICIAN'):
                newly_unlocked.append('THE_TECHNICIAN')
        
        return newly_unlocked
    
    def _unlock_achievement(self, user_id: int, achievement_key: str) -> bool:
        """
        Internal method to unlock an achievement for a user.
        
        Args:
            user_id: The user's ID
            achievement_key: The achievement key to unlock
        
        Returns:
            bool: True if unlocked successfully, False otherwise
        """
        try:
            achievement = Achievement.query.filter_by(key=achievement_key).first()
            if not achievement:
                self._log_error(f"Achievement {achievement_key} not found in database")
                return False
            
            # Check if already unlocked
            existing = UserAchievement.query.filter_by(
                user_id=user_id,
                achievement_id=achievement.id
            ).first()
            
            if existing:
                self._log_debug(f"Achievement {achievement_key} already unlocked for user {user_id}")
                return False
            
            # Create the unlock record
            new_unlock = UserAchievement(user_id=user_id, achievement_id=achievement.id)
            self.add(new_unlock)
            
            if self.commit():
                self._log_info(f"Unlocked achievement {achievement_key} for user {user_id}")
                flash(
                    f"{achievement.icon}|Achievement Unlocked: {achievement.name}! ({achievement.description})",
                    'success'
                )
                return True
            return False
            
        except Exception as e:
            self._log_error(f"Failed to unlock achievement {achievement_key}: {str(e)}")
            self.rollback()
            return False
    
    def unlock_achievement(self, user_id: int, achievement_key: str) -> bool:
        """
        Manually unlock an achievement for a user.
        
        Args:
            user_id: The user's ID
            achievement_key: The achievement key to unlock
        
        Returns:
            bool: True if successful, False otherwise
        """
        self._log_info(f"Manually unlocking {achievement_key} for user {user_id}")
        return self._unlock_achievement(user_id, achievement_key)
    
    def get_user_achievements(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get all achievements for a user, both unlocked and locked.
        
        Args:
            user_id: The user's ID
        
        Returns:
            List of dictionaries containing achievement data with unlock status
        
        Example:
            >>> service = AchievementService()
            >>> achievements = service.get_user_achievements(user_id=1)
            >>> for ach in achievements:
            ...     print(f"{ach['name']}: {'✓' if ach['unlocked'] else '✗'}")
        """
        self._log_debug(f"Getting achievements for user {user_id}")
        
        # Get all achievements
        all_achievements = Achievement.query.all()
        
        # Get user's unlocked achievements
        user_achievements = UserAchievement.query.filter_by(user_id=user_id).all()
        unlocked_ids = {ua.achievement_id for ua in user_achievements}
        unlocked_map = {ua.achievement_id: ua for ua in user_achievements}
        
        result = []
        for achievement in all_achievements:
            unlocked = achievement.id in unlocked_ids
            data = {
                'id': achievement.id,
                'key': achievement.key,
                'name': achievement.name,
                'description': achievement.description,
                'category': achievement.category,
                'icon': achievement.icon,
                'unlocked': unlocked,
                'unlocked_at': unlocked_map[achievement.id].unlocked_at if unlocked else None
            }
            result.append(data)
        
        return result
    
    def get_progress(self, user_id: int, achievement_key: str) -> Dict[str, Any]:
        """
        Get progress towards a specific achievement.
        
        Args:
            user_id: The user's ID
            achievement_key: The achievement key to check progress for
        
        Returns:
            Dictionary containing:
                - current: Current progress value
                - target: Target value needed
                - percentage: Progress percentage (0-100)
                - unlocked: Whether achievement is unlocked
        """
        self._log_debug(f"Getting progress for {achievement_key}")
        
        user = User.query.get(user_id)
        if not user:
            return {'current': 0, 'target': 0, 'percentage': 0, 'unlocked': False}
        
        # Check if already unlocked
        unlocked_keys = {ua.achievement.key for ua in user.user_achievements}
        unlocked = achievement_key in unlocked_keys
        
        # Get achievement definition
        definition = ACHIEVEMENT_DEFINITIONS.get(achievement_key, {})
        target = definition.get('target', 1)
        
        # Determine current progress based on achievement type
        current = 0
        
        if 'STREAK' in achievement_key:
            current = user.streak_days
        elif achievement_key == 'GOAL_CRUSHER':
            current = user.goals.filter_by(status='completed').count()
        elif 'READ' in achievement_key:
            current = len(user.read_articles)
        elif achievement_key == 'THE_TECHNICIAN':
            current = min(len(user.tool_usages), 1)  # Binary: used or not
        elif 'BANKROLL' in achievement_key:
            from ..services import BankrollService
            bankroll_service = BankrollService()
            bankroll_data = bankroll_service.get_bankroll_breakdown(user_id)
            current = float(bankroll_data.get('total_bankroll', 0))
        
        percentage = min(100, (current / target * 100) if target > 0 else 100) if not unlocked else 100
        
        return {
            'current': current,
            'target': target,
            'percentage': percentage,
            'unlocked': unlocked
        }
    
    def update_streak(self, user: User) -> bool:
        """
        Update the user's activity streak based on the current date.
        
        This should be called after any user action that counts as "activity"
        (e.g., logging a transaction, updating bankroll).
        
        Args:
            user: The User object to update
        
        Returns:
            bool: True if streak was updated, False if already updated today
        
        Example:
            >>> service = AchievementService()
            >>> user = current_user
            >>> if service.update_streak(user):
            ...     print(f"Streak: {user.streak_days} days!")
        """
        self._log_debug(f"Updating streak for user {user.id}")
        
        today = date.today()
        
        # If the last activity was already today, do nothing
        if user.last_activity_date == today:
            self._log_debug("Already updated today")
            return False
        
        if user.last_activity_date == today - timedelta(days=1):
            # Active yesterday, so increment the streak
            user.streak_days += 1
            self._log_info(f"Streak incremented to {user.streak_days} for user {user.id}")
        else:
            # Streak is broken or it's the first activity, reset to 1
            user.streak_days = 1
            self._log_info(f"Streak reset to 1 for user {user.id}")
        
        user.last_activity_date = today
        
        # Check for streak achievements after updating
        self.check_achievements(user)
        
        return True
    
    def award_badge(self, user_id: int, badge_name: str, badge_description: str) -> bool:
        """
        Award a custom badge to a user.
        
        Args:
            user_id: The user's ID
            badge_name: Name of the badge
            badge_description: Description of the badge
        
        Returns:
            bool: True if successful, False otherwise
        """
        self._log_info(f"Awarding badge '{badge_name}' to user {user_id}")
        
        # This is a placeholder for future custom badge functionality
        # For now, we only support predefined achievements
        self._log_debug("Custom badges not yet implemented")
        return False
    
    def check_milestone_achievements(self, user_id: int) -> List[str]:
        """
        Check only milestone-based achievements (bankroll, goals, etc.).
        
        This is useful for checking achievements after specific events
        like completing a goal or reaching a bankroll milestone.
        
        Args:
            user_id: The user's ID
        
        Returns:
            List of newly unlocked milestone achievement keys
        """
        self._log_debug(f"Checking milestone achievements for user {user_id}")
        
        user = User.query.get(user_id)
        if not user:
            return []
        
        # Use the main check_achievements method but filter results
        all_unlocked = self.check_achievements(user)
        
        # Filter to only milestone achievements
        milestone_categories = ['Milestone']
        milestone_unlocked = [
            key for key in all_unlocked
            if ACHIEVEMENT_DEFINITIONS.get(key, {}).get('category') in milestone_categories
        ]
        
        return milestone_unlocked
