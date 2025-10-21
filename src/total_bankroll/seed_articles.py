import os
from total_bankroll import create_app, db
from total_bankroll.models import Article
from datetime import datetime, UTC

def seed_articles(app, md_directory):
    with app.app_context():
        print(f"Using database: {app.config['SQLALCHEMY_DATABASE_URI']}")
        # Create tables if they don't exist
        db.create_all()
        print(f"Database tables created or verified")
        print(f"Checking directory: {md_directory}")
        print(f"Directory exists: {os.path.exists(md_directory)}")
        print(f"Directory is dir: {os.path.isdir(md_directory)}")
        if not os.path.exists(md_directory):
            print(f"Error: Directory {md_directory} does not exist")
            return
        print(f"Reading files from {md_directory}")
        for filename in os.listdir(md_directory):
            if filename.endswith('.md'):
                print(f"Processing file: {filename}")
                with open(os.path.join(md_directory, filename), 'r', encoding='utf-8') as f:
                    content_md = f.read()
                    title = filename.replace('.md', '').replace('-', ' ').title()
                    print(f"Adding article: {title}")
                    article = Article(
                        title=title,
                        content_md=content_md,
                        date_published=datetime.now(UTC)
                    )
                    db.session.add(article)
        try:
            print("Committing changes to database")
            db.session.commit()
            print("Articles seeded successfully")
        except Exception as e:
            print(f"Error committing to database: {e}")
            db.session.rollback()

if __name__ == '__main__':
    app = create_app(config_name='production')
    md_dir = '/home/pythonpydev/total_bankroll/resources/articles/markdown'
    seed_articles(app, md_dir)
