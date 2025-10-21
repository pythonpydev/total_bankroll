from flask import Blueprint, render_template
from ..extensions import db
from ..models import Article  # Assumes Article model is defined in models.py

articles_bp = Blueprint('articles', __name__, url_prefix='/strategy/articles')

@articles_bp.route('/')
def index():
    """Display a list of articles."""
    articles = Article.query.order_by(Article.date_published.desc()).all()
    return render_template('articles.html', articles=articles)

@articles_bp.route('/<int:id>')
def view(id):
    """Display a single article."""
    article = Article.query.get_or_404(id)
    return render_template('article.html', article=article, content=article.render_content())
