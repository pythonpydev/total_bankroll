import os
import sys
import logging
import inspect # Added for debugging
import markdown
import frontmatter as fm
from dotenv import load_dotenv
from sqlalchemy.exc import OperationalError

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# --- Debugging frontmatter import ---
try:
    logger.debug(f"frontmatter module loaded from: {fm.__file__}")
    # Get members of the module that are functions and start with 'load' or 'read'
    relevant_functions = [
        name for name, obj in inspect.getmembers(fm, inspect.isfunction)
        if name.startswith('load') or name.startswith('read') or name.startswith('dump')
    ]
    logger.debug(f"Relevant functions in frontmatter module: {relevant_functions}")
except AttributeError:
    logger.error("Could not inspect 'fm' (frontmatter) module. It might not be a module or is corrupted.")
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
from total_bankroll.models import Article, Tag
from datetime import datetime, UTC

def seed_articles(app, md_directory):
    with app.app_context():
        logger.debug(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
        if not os.path.exists(md_directory):
            logger.error(f"Directory {md_directory} does not exist")
            return
        try:
            existing_articles = {article.title: article for article in Article.query.all()}
        except OperationalError as e:
            logger.error(f"Database connection error: {e}")
            sys.exit(1)
        for filename in os.listdir(md_directory):
            if filename.endswith(('.md', '.html')):
                with open(os.path.join(md_directory, filename), 'r', encoding='utf-8') as f:
                    post = fm.load(f)
                    raw_content = post.content
                    new_content_html = None
                    content_md = None
                    content_html = None # Initialize content_html to None
                    
                    if filename.endswith('.html'):
                        content_html = raw_content
                        title = filename.replace('.html', '').replace('-', ' ').title()
                    else:  # .md file
                        content_md = raw_content
                        new_content_html = markdown.markdown(raw_content, extensions=['tables'])
                        title = filename.replace('.md', '').replace('-', ' ').title()

                    tag_names = post.metadata.get('tags', [])
                    if title in existing_articles:
                        # Article exists, check for content changes
                        article_to_update = existing_articles[title]
                        source_content_changed = (content_md and article_to_update.content_md != content_md) or \
                                                (content_html and not content_md and article_to_update.content_html != content_html)

                        if source_content_changed:
                            logger.info(f"Updating article: {title}")
                            article_to_update.content_md = content_md
                            article_to_update.content_html = new_content_html or content_html

                            # Update tags
                            article_to_update.tags.clear()
                            for tag_name in tag_names:
                                tag = Tag.query.filter_by(name=tag_name).first()
                                if not tag:
                                    tag = Tag(name=tag_name)
                                    db.session.add(tag)
                                article_to_update.tags.append(tag)
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
                        for tag_name in tag_names:
                            tag = Tag.query.filter_by(name=tag_name).first()
                            if not tag:
                                tag = Tag(name=tag_name)
                                db.session.add(tag)
                            article.tags.append(tag)

                        db.session.add(article)
        try:
            db.session.commit()
            logger.info("Articles seeded successfully")
        except Exception as e:
            logger.error(f"Error committing to database: {e}")
            db.session.rollback()

if __name__ == '__main__':
    config_name = 'development' if os.getenv('FLASK_ENV') == 'development' else 'production'
    logger.debug(f"Creating app. FLASK_ENV is: {os.getenv('FLASK_ENV')}")
    app = create_app() # create_app determines config from FLASK_ENV
    md_dir = os.path.join(basedir, '../../resources/articles/markdown')  # /home/pythonpydev/total_bankroll/resources/articles/markdown
    logger.debug(f"Seeding articles from: {md_dir}")
    seed_articles(app, md_dir)