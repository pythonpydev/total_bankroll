import os
import sys
import logging
import markdown
from dotenv import load_dotenv

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Add project directory to sys.path
basedir = os.path.abspath(os.path.dirname(__file__))  # /home/ed/MEGA/total_bankroll/src/total_bankroll
project_home = os.path.join(basedir, '..')  # /home/ed/MEGA/total_bankroll/src
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Load .env file from project root or src/
env_paths = [
    os.path.join(basedir, '../../.env'),  # /home/ed/MEGA/total_bankroll/.env
    os.path.join(basedir, '../.env')      # /home/ed/MEGA/total_bankroll/src/.env
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
from total_bankroll.models import Article
from datetime import datetime, UTC

def seed_articles(app, md_directory):
    with app.app_context():
        logger.debug(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
        db.create_all()
        if not os.path.exists(md_directory):
            logger.error(f"Directory {md_directory} does not exist")
            return
        existing_titles = {article.title for article in Article.query.all()}
        for filename in os.listdir(md_directory):
            if filename.endswith(('.md', '.html')):
                with open(os.path.join(md_directory, filename), 'r', encoding='utf-8') as f:
                    raw_content = f.read()
                    content_html = None
                    content_md = None
                    
                    if filename.endswith('.html'):
                        content_html = raw_content
                        title = filename.replace('.html', '').replace('-', ' ').title()
                    else: # .md file
                        content_md = raw_content
                        content_html = markdown.markdown(raw_content, extensions=['tables'])
                        title = filename.replace('.md', '').replace('-', ' ').title()

                    if title in existing_titles:
                        logger.debug(f"Skipping duplicate article: {title}")
                        continue

                    article = Article(
                        title=title,
                        content_md=content_md,
                        content_html=content_html,
                        date_published=datetime.now(UTC)
                    )
                    db.session.add(article)
                    existing_titles.add(title)
        try:
            db.session.commit()
            logger.info("Articles seeded successfully")
        except Exception as e:
            logger.error(f"Error committing to database: {e}")
            db.session.rollback()

if __name__ == '__main__':
    config_name = 'development' if os.getenv('FLASK_ENV') == 'development' else 'production'
    logger.debug(f"Creating app with config: {config_name}")
    app = create_app(config_name=config_name)
    md_dir = os.path.join(basedir, '../../resources/articles/markdown')  # /home/ed/MEGA/total_bankroll/resources/articles/markdown
    logger.debug(f"Seeding articles from: {md_dir}")
    seed_articles(app, md_dir)