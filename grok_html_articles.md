To enhance your articles database by allowing preformatted HTML content (in addition to Markdown), you can modify the seeding process to handle both `.md` and `.html` files. This way, files like `player_types_article.html` can be stored directly in the `content_html` field of the `Article` model, bypassing Markdown conversion. The `render_content()` method will prioritize `content_html` if present, falling back to rendering `content_md` if not.

This approach keeps the database flexible:
- `.md` files are stored in `content_md` and rendered to HTML on-the-fly.
- `.html` files are stored in `content_html` and used directly (with sanitization for security).
- You can place `.html` files (e.g., `player_types_article.html`) in the same directory as `.md` files (`/home/ed/MEGA/total_bankroll/resources/articles/markdown/`), and the seeding script will handle them automatically.

Below, I’ll provide the updated `seed_articles.py` and `models.py` files to implement this. The changes are minimal and build on your existing code. After updating, you can run the seeding script to populate the database with preformatted HTML.

### Step 1: Update `seed_articles.py`
Modify `/home/ed/MEGA/total_bankroll/src/total_bankroll/seed_articles.py` to process both `.md` and `.html` files. For `.html` files, store the content directly in `content_html`.

```python
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
                    existing_article = Article.query.filter_by(title=title).first()
                    if existing_article:
                        print(f"Skipping existing article: {title}")
                        continue
                    article = Article(
                        title=title,
                        content_md=content_md,
                        date_published=datetime.now(UTC)
                    )
                    db.session.add(article)
            elif filename.endswith('.html'):
                with open(os.path.join(md_directory, filename), 'r', encoding='utf-8') as f:
                    content_html = f.read()
                    title = filename.replace('.html', '').replace('-', ' ').title()
                    existing_article = Article.query.filter_by(title=title).first()
                    if existing_article:
                        print(f"Skipping existing article: {title}")
                        continue
                    article = Article(
                        title=title,
                        content_html=content_html,
                        date_published=datetime.now(UTC)
                    )
                    db.session.add(article)
        db.session.commit()
        print("Articles seeded successfully")

if __name__ == '__main__':
    app = create_app(config_name='production')
    md_dir = 'resources/articles/markdown'
    seed_articles(app, md_dir)
```

- **Changes**:
  - Added logic to handle `.html` files, storing their content in `content_html`.
  - Added a check to skip existing articles (based on `title`) to prevent duplicates during reseeding.
  - For `.md` files, continues to store in `content_md` as before.
  - The directory is relative to the script (`resources/articles/markdown`), but you can adjust `md_dir` to an absolute path if needed (e.g., `/home/ed/MEGA/total_bankroll/resources/articles/markdown`).

- **Action**:
  - Save this as `/home/ed/MEGA/total_bankroll/src/total_bankroll/seed_articles.py`.
  - Set permissions: `chmod 644 /home/ed/MEGA/total_bankroll/src/total_bankroll/seed_articles.py`.

#### Step 2: Update `models.py`
Modify `/home/ed/MEGA/total_bankroll/src/total_bankroll/models.py` to update the `render_content()` method. It will return `content_html` if available (for preformatted HTML), else convert `content_md` to HTML. Sanitize `content_html` with `bleach` to ensure security and consistency with `_styles.css` (e.g., allowing poker hand `<span>` classes and table tags).

```python:disable-run
from flask_security import UserMixin
from .extensions import db
from datetime import datetime, UTC
from flask_security.utils import hash_password
import markdown
import bleach
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=True)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    last_login_at = db.Column(db.DateTime, nullable=True)
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)
    is_confirmed = db.Column(db.Boolean, default=False, nullable=False)
    confirmed_on = db.Column(db.DateTime, nullable=True)
    default_currency_code = db.Column(db.String(3), db.ForeignKey('currency.code'), nullable=False, default='USD')
    otp_secret = db.Column(db.String(16))
    otp_enabled = db.Column(db.Boolean, default=False, nullable=False)

    def get_id(self):
        return self.fs_uniquifier

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = hash_password(password)

class OAuth(db.Model):
    __tablename__ = 'oauth'
    id = db.Column(db.Integer, primary_key=True)
    provider = db.Column(db.String(50), nullable=False)
    provider_user_id = db.Column(db.String(255), nullable=False)
    token = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', backref=db.backref('oauth', lazy='dynamic'))

class Sites(db.Model):
    __tablename__ = 'sites'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    display_order = db.Column(db.Integer, nullable=False, server_default='0')
    user = db.relationship('User', backref=db.backref('sites', lazy='dynamic'))

class Assets(db.Model):
    __tablename__ = 'assets'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    display_order = db.Column(db.Integer, nullable=False, server_default='0')
    user = db.relationship('User', backref=db.backref('assets', lazy='dynamic'))

class Deposits(db.Model):
    __tablename__ = 'deposits'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    last_updated = db.Column(db.DateTime, nullable=False)
    currency = db.Column(db.String(3), db.ForeignKey('currency.code'), nullable=False, default='USD')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('deposits', lazy='dynamic'))

class Drawings(db.Model):
    __tablename__ = 'drawings'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    last_updated = db.Column(db.DateTime, nullable=False)
    currency = db.Column(db.String(3), db.ForeignKey('currency.code'), nullable=False, default='USD')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('drawings', lazy='dynamic'))

class SiteHistory(db.Model):
    __tablename__ = 'site_history'
    id = db.Column(db.Integer, primary_key=True)
    site_id = db.Column(db.Integer, db.ForeignKey('sites.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), db.ForeignKey('currency.code'), nullable=False)
    recorded_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    site = db.relationship('Sites', backref=db.backref('history', lazy='dynamic'))
    user = db.relationship('User', backref=db.backref('site_history', lazy='dynamic'))

class AssetHistory(db.Model):
    __tablename__ = 'asset_history'
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), db.ForeignKey('currency.code'), nullable=False)
    recorded_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    asset = db.relationship('Assets', backref=db.backref('history', lazy='dynamic'))
    user = db.relationship('User', backref=db.backref('asset_history', lazy='dynamic'))

class Currency(db.Model):
    __tablename__ = 'currency'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    rate = db.Column(db.Numeric(10, 6), nullable=False)
    code = db.Column(db.String(3), nullable=False, unique=True)
    symbol = db.Column(db.String(5), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

class CashStakes(db.Model):
    __tablename__ = 'cash_stakes'
    id = db.Column(db.Integer, primary_key=True)
    small_blind = db.Column(db.Numeric(10, 2), nullable=False)
    big_blind = db.Column(db.Numeric(10, 2), nullable=False)
    min_buy_in = db.Column(db.Numeric(10, 2), nullable=False)
    max_buy_in = db.Column(db.Numeric(10, 2), nullable=False)

class Article(db.Model):
    __tablename__ = 'articles'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content_md = db.Column(db.Text, nullable=False)
    content_html = db.Column(db.Text, nullable=True)
    date_published = db.Column(db.DateTime, nullable=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    author = relationship('User', backref='articles')

    def render_content(self):
        html = markdown.markdown(self.content_md, extensions=['tables'])
        allowed_tags = list(bleach.sanitizer.ALLOWED_TAGS) + ['p', 'h1', 'h2', 'h3', 'h4', 'ul', 'ol', 'li', 'strong', 'em', 'a', 'span', 'table', 'tr', 'th', 'td', 'thead', 'tbody']
        allowed_attributes = {'a': ['href'], 'span': ['class'], 'table': ['class'], 'th': ['class'], 'td': ['class']}
        return bleach.clean(html, tags=allowed_tags, attributes=allowed_attributes)

class Topic(db.Model):
    __tablename__ = 'topics'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

article_topics = db.Table('article_topics',
    db.Column('article_id', db.Integer, db.ForeignKey('articles.id'), primary_key=True),
    db.Column('topic_id', db.Integer, db.ForeignKey('topics.id'), primary_key=True)
)
</DOCUMENT>

<DOCUMENT filename="articles.html">
{% extends "base.html" %}
{% block content %}
<section class="page-section" id="articles">
    <div class="container px-4 px-lg-5">
        <h2 class="text-center mb-5">Strategy Articles</h2>
        <div class="row gx-4 gx-lg-5">
            {% if articles %}
                {% for article in articles %}
                <div class="col-lg-4 mb-4">
                    <div class="card h-100 shadow-sm">
                        <div class="card-body">
                            <h5 class="card-title">{{ article.title }}</h5>
                            <div class="card-text table-responsive">
                                {{ article.render_content() | truncate_html(150) | safe }}
                            </div>
                            <p class="card-text"><small class="text-muted">Published on {{ article.date_published.strftime('%B %d, %Y') }}</small></p>
                            <a href="{{ url_for('articles.view', id=article.id) }}" class="btn btn-primary">Read More</a>
                        </div>
                    </div>
                </div>
                {% endfor %}
            {% else %}
                <div class="col-12 text-center">
                    <p class="lead">No articles found. Check back soon!</p>
                </div>
            {% endif %}
        </div>
    </div>
</section>
{% endblock %}
</DOCUMENT>

<DOCUMENT filename="article.html">
{% extends "base.html" %}
{% block content %}
<section class="page-section article-section" id="article">
    <div class="container px-4 px-lg-5">
        <div class="row justify-content-center">
            <div class="col-lg-8 col-md-10">
                <header class="article-header mb-4">
                    <h1 class="article-title">{{ article.title }}</h1>
                    <p class="article-meta text-muted">
                        <i class="bi bi-calendar3 me-1"></i> Published on {{ article.date_published.strftime('%B %d, %Y') }}
                        {% if article.author %}
                        | <i class="bi bi-person me-1"></i> By {{ article.author.username }}
                        {% endif %}
                    </p>
                </header>
                <hr class="article-divider">
                <div class="article-content shadow-sm p-4 bg-white dark-bg">
                    {{ content | safe }}
                </div>
                <div class="article-footer mt-4">
                    <a href="{{ url_for('articles.index') }}" class="btn btn-outline-secondary">
                        <i class="bi bi-arrow-left me-1"></i> Back to Articles
                    </a>
                </div>
            </div>
        </div>
    </div>
</section>
{% endblock %}</DOCUMENT>

<DOCUMENT filename="player_types_article.html">
{% extends "base.html" %}
{% from "_macros.html" import page_header %}

{% block content %}
{{ page_header('Poker Player Archetypes', 'A guide to identifying and exploiting different player types in PLO.') }}

<section class="page-section">
    <div class="container">
        <div class="row justify-content-center">
            <div class="col-lg-9">
                <p class="lead text-center mb-5">This is a detailed taxonomy of poker-player archetypes (fish, TAG, LAG, NIT, station, etc.), how they tend to play (especially in Pot Limit Omaha), and how to exploit them. In practice, many players are hybrids or evolve over time, so these are idealized types.</p>

                <h2 class="mb-3">Basic Classification Axes</h2>
                <p>Most poker "types" can be described along two axes: how selective they are about entering pots (Tight vs. Loose) and how often they bet/raise vs. check/call (Aggressive vs. Passive).</p>

                <div class="table-responsive shadow-sm rounded mb-5">
                    <table class="table table-bordered mb-0">
                        <thead class="table-dark">
                            <tr>
                                <th>Style</th>
                                <th>Aggressive</th>
                                <th>Passive</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <th class="table-light">Tight</th>
                                <td><strong>Tight-Aggressive (TAG) / NIT</strong></td>
                                <td><strong>Tight-Passive (Rock)</strong></td>
                            </tr>
                            <tr>
                                <th class="table-light">Loose</th>
                                <td><strong>Loose-Aggressive (LAG) / Maniac</strong></td>
                                <td><strong>Loose-Passive (Calling Station / Fish)</strong></td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                <hr class="divider-light" />

                <h2 class="mt-5 mb-4">Archetypes and Their Behaviors</h2>

                <!-- Loose-Passive -->
                <div class="card mb-4 shadow-sm">
                    <div class="card-header"><h4 class="player-light-blue">1. Loose-Passive ("Fish", "Calling Station")</h4></div>
                    <div class="card-body">
                        <p>Plays many hands, rarely raises, and doesn’t fold easily. They are called "fish" because they are easier prey, because they are easier prey, ...(truncated 5029 characters)...                    </tr>
                        </thead>
                        <tbody>
                            <tr class="player-light-blue">
                                <td><strong>Station / Fish</strong></td>
                                <td>Loose-Passive</td>
                                <td>Calls a lot, rarely folds</td>
                                <td>Value-bet heavily, avoid bluffing.</td>
                            </tr>
                            <tr class="player-light-blue">
                                <td><strong>Weak Limper</strong></td>
                                <td>Loose-Passive</td>
                                <td>Limp many hands preflop</td>
                                <td>Raise to isolate them with good holdings.</td>
                            </tr>
                            <tr class="player-orange">
                                <td><strong>LAG / Aggro Fish</strong></td>
                                <td>Loose-Aggressive</td>
                                <td>Raises a lot, applies pressure</td>
                                <td>Tighten up, trap, and call down selectively.</td>
                            </tr>
                            <tr class="player-purple">
                                <td><strong>TAG (Reg)</strong></td>
                                <td>Tight-Aggressive</td>
                                <td>Selective, balanced aggression</td>
                                <td>Use position, bet/polarize carefully.</td>
                            </tr>
                            <tr class="player-white">
                                <td><strong>NIT / Rock</strong></td>
                                <td>Tight-Passive</td>
                                <td>Enters few hands, rarely bluffs</td>
                                <td>Steal blinds, but respect their aggression.</td>
                            </tr>
                            <tr class="player-red">
                                <td><strong>Maniac</strong></td>
                                <td>Loose-Aggressive</td>
                                <td>Always bets/raises, high variance</td>
                                <td>Tighten up, let them build the pot, and trap.</td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                <div class="text-center mt-5">
                    <a href="{{ url_for('tools.tools_page') }}" class="btn btn-primary">Back to Tools</a>
                </div>
            </div>
        </div>
    </div>
</section>

{% endblock %}</DOCUMENT>

 Can you explain why the tables are not rendering correctly on the articles page?  I have attached all the relevant files.  The tables are rendering fine on the individual article page.  The problem is that the tables are not rendering correctly on the articles page, i.e. the card previews.  The tables are rendering as text, not as tables.  I think the problem is with the truncate_html function.  Can you update the truncate_html function to handle tables?
```
