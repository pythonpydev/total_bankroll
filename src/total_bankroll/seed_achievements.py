import os
import sys
import logging
from dotenv import load_dotenv
from sqlalchemy.exc import OperationalError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add project directory to sys.path
basedir = os.path.abspath(os.path.dirname(__file__))  # /home/pythonpydev/total_bankroll/src/total_bankroll
project_home = os.path.join(basedir, '..')  # /home/pythonpydev/total_bankroll/src
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Load .env file from project root or src/
env_paths = [
    os.path.join(basedir, '../../.env'),  # /home/pythonpydev/total_bankroll/.env
    os.path.join(basedir, '../.env')      # /home/pythonpydev/total_bankroll/src/.env
]
env_loaded = False
for env_path in env_paths:
    if os.path.exists(env_path):
        logger.debug(f"Loading .env from: {env_path}")
        load_dotenv(env_path, override=True)
        env_loaded = True
        break
if not env_loaded:
    logger.error(f"No .env file found at {env_paths}")
    sys.exit(1)

from total_bankroll import create_app, db
from total_bankroll.models import Achievement
try:
    from total_bankroll.achievements import ACHIEVEMENT_DEFINITIONS
except ImportError:
    logger.error("ACHIEVEMENT_DEFINITIONS not found in total_bankroll.achievements")
    sys.exit(1)

def seed_achievements(app):
    """Seeds the achievements table from the definitions."""
    with app.app_context():
        try:
            existing_keys = {ach.key for ach in Achievement.query.all()}
        except OperationalError as e:
            logger.error(f"Database connection error: {e}")
            sys.exit(1)
        for key, data in ACHIEVEMENT_DEFINITIONS.items():
            if key not in existing_keys:
                new_achievement = Achievement(key=key, **data)
                db.session.add(new_achievement)
                logger.info(f"Adding achievement: {key}")
        try:
            db.session.commit()
            logger.info("Achievements seeded successfully")
        except Exception as e:
            logger.error(f"Error committing to database: {e}")
            db.session.rollback()

if __name__ == '__main__':
    config_name = os.getenv('FLASK_ENV', 'development')
    logger.debug(f"Creating app. FLASK_ENV is: {os.getenv('FLASK_ENV')}")
    app = create_app() # create_app determines config from FLASK_ENV
    seed_achievements(app)