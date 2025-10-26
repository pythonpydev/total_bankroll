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
        existing_articles = {article.title: article for article in Article.query.all()}
        for filename in os.listdir(md_directory):
            if filename.endswith(('.md', '.html')):
                with open(os.path.join(md_directory, filename), 'r', encoding='utf-8') as f:
                    raw_content = f.read()
                    new_content_html = None
                    content_md = None
                    
                    if filename.endswith('.html'):
                        content_html = raw_content
                        title = filename.replace('.html', '').replace('-', ' ').title()
                    else: # .md file
                        content_md = raw_content
                        new_content_html = markdown.markdown(raw_content, extensions=['tables'])
                        title = filename.replace('.md', '').replace('-', ' ').title()

                    if title in existing_articles:
                        # Article exists, check for content changes
                        article_to_update = existing_articles[title]
                        # Compare based on the source content (MD or HTML)
                        source_content_changed = (content_md and article_to_update.content_md != content_md) or \
                                                 (content_html and not content_md and article_to_update.content_html != content_html)

                        if source_content_changed:
                            logger.info(f"Updating article: {title}")
                            article_to_update.content_md = content_md
                            article_to_update.content_html = new_content_html or content_html
                        else:
                            logger.debug(f"Skipping unchanged article: {title}")
                    else:
                        # This is a new article
                        logger.info(f"Adding new article: {title}")
                        article = Article(
                            title=title,
                            content_md=content_md,
                            content_html=new_content_html or content_html,
                            date_published=datetime.now(UTC)
                        )
                        db.session.add(article)
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