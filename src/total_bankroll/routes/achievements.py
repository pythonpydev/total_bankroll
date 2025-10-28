from flask import Blueprint, render_template
from flask_security import login_required, current_user
from ..models import Achievement

achievements_bp = Blueprint('achievements', __name__, url_prefix='/achievements')

@achievements_bp.route('/')
@login_required
def index():
    """Displays all achievements and the user's unlocked status."""
    all_achievements = Achievement.query.order_by(Achievement.category, Achievement.name).all()
    unlocked_achievement_keys = {ua.achievement.key for ua in current_user.user_achievements}

    # Augment each achievement object with its unlocked status and progress
    for ach in all_achievements:
        ach.unlocked = ach.key in unlocked_achievement_keys
        ach.current_progress = 0
        ach.progress_percent = 0

        if not ach.unlocked and ach.target:
            if ach.category == 'Consistency':
                ach.current_progress = current_user.streak_days
            elif ach.category == 'Study' and 'READ' in ach.key:
                ach.current_progress = len(current_user.read_articles)
            # Add other categories here as needed

            if ach.target > 0:
                ach.progress_percent = min(100, (ach.current_progress / ach.target) * 100)

    return render_template('info/achievements.html',
                           achievements=all_achievements,
                           title="Your Achievements")