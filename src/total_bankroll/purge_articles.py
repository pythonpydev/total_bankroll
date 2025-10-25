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
else:
    logger.error(".env file not found!")
    sys.exit(1)

from total_bankroll import create_app, db
from total_bankroll.models import Article

def purge_articles(app):
    """Deletes all records from the articles table."""
    with app.app_context():
        try:
            num_deleted = db.session.query(Article).delete()
            db.session.commit()
            logger.info(f"Successfully purged {num_deleted} articles from the database.")
        except Exception as e:
            logger.error(f"Error purging articles: {e}")
            db.session.rollback()

if __name__ == '__main__':
    config_name = os.getenv('FLASK_ENV', 'development')
    app = create_app(config_name=config_name)
    purge_articles(app)