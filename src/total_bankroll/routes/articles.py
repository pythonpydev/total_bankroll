from flask import Blueprint, render_template, flash, redirect, url_for
from flask_security import login_required, current_user
from ..extensions import db
from ..models import Article, UserReadArticle
from ..achievements import check_and_award_achievements

articles_bp = Blueprint('articles', __name__, url_prefix='/strategy/articles')

@articles_bp.route('/')
@login_required
def index():
    """Display a list of articles."""
    articles = Article.query.order_by(Article.date_published.desc()).all()
    return render_template('articles.html', articles=articles)

@articles_bp.route('/<int:id>')
@login_required
def view(id):
    """Display a single article."""
    article = Article.query.get_or_404(id)
    has_read = UserReadArticle.query.filter_by(user_id=current_user.id, article_id=article.id).first() is not None
    return render_template('article.html', article=article, has_read=has_read)

@articles_bp.route('/<int:article_id>/mark-as-read', methods=['POST'])
@login_required
def mark_as_read(article_id):
    """Mark an article as read for the current user."""
    # Check if it's already marked as read to prevent duplicates
    already_read = UserReadArticle.query.filter_by(user_id=current_user.id, article_id=article_id).first()
    if not already_read:
        new_read_entry = UserReadArticle(user_id=current_user.id, article_id=article_id)
        db.session.add(new_read_entry)
        db.session.commit()
        check_and_award_achievements(current_user) # Check for new achievements
        flash("You've marked this article as read!", "info")
    return redirect(url_for('articles.view', id=article_id))
