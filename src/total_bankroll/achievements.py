from datetime import date, timedelta
from flask import flash
from .models import db, User, Achievement, UserAchievement
from .utils import get_user_bankroll_data

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
}

def check_and_award_achievements(user: User):
    """
    Checks all achievement conditions for a user and awards them if met.
    This function is designed to be expanded with more achievement types.
    """
    # Get achievements the user has already unlocked to avoid re-awarding.
    bankroll_data = get_user_bankroll_data(user.id)
    unlocked_keys = {ua.achievement.key for ua in user.user_achievements}

    # --- 1. Check Streak Achievements ---
    streak_achievements = {
        'STREAK_3_DAY': 3,
        'STREAK_7_DAY': 7,
        'STREAK_30_DAY': 30
    }
    for key, required_streak in streak_achievements.items():
        if user.streak_days >= required_streak and key not in unlocked_keys:
            achievement = Achievement.query.filter_by(key=key).first()
            if achievement:
                new_unlock = UserAchievement(user_id=user.id, achievement_id=achievement.id)
                db.session.add(new_unlock)
                flash(f"{achievement.icon}|Achievement Unlocked: {achievement.name}! ({achievement.description})", 'success')

    # --- 2. Check Bankroll Milestones ---
    bankroll_milestones = {
        'BANKROLL_1K': 1000,
        'BANKROLL_10K': 10000
    }
    total_bankroll = bankroll_data.get('total_bankroll', 0.0)

    for key, required_amount in bankroll_milestones.items():
        if total_bankroll >= required_amount and key not in unlocked_keys:
            achievement = Achievement.query.filter_by(key=key).first()
            if achievement:
                new_unlock = UserAchievement(user_id=user.id, achievement_id=achievement.id)
                db.session.add(new_unlock)
                flash(f"{achievement.icon}|Achievement Unlocked: {achievement.name}! ({achievement.description})", 'success')

    # --- 3. Check Goal Achievements ---
    completed_goal_count = user.goals.filter_by(status='completed').count()
    if completed_goal_count > 0 and 'GOAL_CRUSHER' not in unlocked_keys:
        achievement = Achievement.query.filter_by(key='GOAL_CRUSHER').first()
        if achievement:
            new_unlock = UserAchievement(user_id=user.id, achievement_id=achievement.id)
            db.session.add(new_unlock)
            flash(f"{achievement.icon}|Achievement Unlocked: {achievement.name}! ({achievement.description})", 'success')

    # --- 4. Check Article Reading Achievements ---
    read_count = len(user.read_articles)
    article_achievements = {
        'READ_1_ARTICLE': 1,
        'READ_10_ARTICLES': 10
    }
    for key, required_reads in article_achievements.items():
        if read_count >= required_reads and key not in unlocked_keys:
            achievement = Achievement.query.filter_by(key=key).first()
            if achievement:
                new_unlock = UserAchievement(user_id=user.id, achievement_id=achievement.id)
                db.session.add(new_unlock)
                flash(f"{achievement.icon}|Achievement Unlocked: {achievement.name}! ({achievement.description})", 'success')

    # --- 5. Check Tool Usage Achievements ---
    tool_usage_count = len(user.tool_usages)
    if tool_usage_count > 0 and 'THE_TECHNICIAN' not in unlocked_keys:
        achievement = Achievement.query.filter_by(key='THE_TECHNICIAN').first()
        if achievement:
            new_unlock = UserAchievement(user_id=user.id, achievement_id=achievement.id)
            db.session.add(new_unlock)
            flash(f"{achievement.icon}|Achievement Unlocked: {achievement.name}! ({achievement.description})", 'success')

    db.session.commit()

def update_user_streak(user: User):
    """
    Updates the user's activity streak based on the current date.
    This should be called after any user action that counts as "activity".
    """
    today = date.today()

    # If the last activity was already today, do nothing.
    if user.last_activity_date == today:
        return

    if user.last_activity_date == today - timedelta(days=1):
        # Active yesterday, so increment the streak.
        user.streak_days += 1
    else:
        # Streak is broken or it's the first activity, reset to 1.
        user.streak_days = 1
    
    user.last_activity_date = today
    check_and_award_achievements(user)