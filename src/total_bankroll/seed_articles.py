import os
from total_bankroll import create_app, db
from total_bankroll.models import Article
from datetime import datetime, UTC

def seed_articles(app, md_directory):
    with app.app_context():
        if not os.path.exists(md_directory):
            print(f"Error: Directory {md_directory} does not exist")
            return
        for filename in os.listdir(md_directory):
            if filename.endswith('.md'):
                with open(os.path.join(md_directory, filename), 'r', encoding='utf-8') as f:
                    content_md = f.read()
                    title = filename.replace('.md', '').replace('-', ' ').title()
                    article = Article(
                        title=title,
                        content_md=content_md,
                        date_published=datetime.now(UTC)
                    )
                    db.session.add(article)
        db.session.commit()
        print("Articles seeded successfully")

if __name__ == '__main__':
    app = create_app()
    md_dir = 'resources/articles/markdown'
    seed_articles(app, md_dir)
