import os
import sys

# Add project directory to sys.path before imports
project_home = '/home/pythonpydev/total_bankroll/src'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

from total_bankroll import create_app, db
from total_bankroll.models import Article
from datetime import datetime, UTC

def seed_articles(app, md_directory):
    with app.app_context():
        db.create_all()
        if not os.path.exists(md_directory):
            print(f"Error: Directory {md_directory} does not exist")
            return
        existing_titles = {article.title for article in Article.query.all()}
        for filename in os.listdir(md_directory):
            if filename.endswith('.md'):
                with open(os.path.join(md_directory, filename), 'r', encoding='utf-8') as f:
                    content_md = f.read()
                    title = filename.replace('.md', '').replace('-', ' ').title()
                    if title in existing_titles:
                        continue
                    article = Article(
                        title=title,
                        content_md=content_md,
                        date_published=datetime.now(UTC)
                    )
                    db.session.add(article)
                    existing_titles.add(title)
        try:
            db.session.commit()
            print("Articles seeded successfully")
        except Exception as e:
            print(f"Error committing to database: {e}")
            db.session.rollback()

if __name__ == '__main__':
    app = create_app(config_name='production')
    md_dir = '/home/pythonpydev/total_bankroll/resources/articles/markdown'
    seed_articles(app, md_dir)