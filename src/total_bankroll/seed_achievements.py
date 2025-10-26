import os
import sys
import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add project directory to sys.path
basedir = os.path.abspath(os.path.dirname(__file__))
project_home = os.path.join(basedir, '..')
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Load .env
env_path = os.path.join(basedir, '../../.env')
if os.path.exists(env_path):
    load_dotenv(env_path)

from total_bankroll import create_app, db
from total_bankroll.models import Achievement
from total_bankroll.achievements import ACHIEVEMENT_DEFINITIONS

def seed_achievements(app):
    """Seeds the achievements table from the definitions."""
    with app.app_context():
        existing_keys = {ach.key for ach in Achievement.query.all()}
        for key, data in ACHIEVEMENT_DEFINITIONS.items():
            if key not in existing_keys:
                new_achievement = Achievement(key=key, **data)
                db.session.add(new_achievement)
                logger.info(f"Adding achievement: {key}")
        db.session.commit()
        logger.info("Achievements seeding complete.")

if __name__ == '__main__':
    config_name = os.getenv('FLASK_ENV', 'development')
    app = create_app(config_name=config_name)
    seed_achievements(app)