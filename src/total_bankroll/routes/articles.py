from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_security import login_required, current_user
from sqlalchemy import or_
from ..models import db, Article, UserReadArticle, Tag
from ..achievements import check_and_award_achievements

articles_bp = Blueprint('articles', __name__, url_prefix='/strategy/articles')

@articles_bp.route('/')
@login_required
def index():
    """Display a list of articles."""
    page = request.args.get('page', 1, type=int)
    per_page = 6  # Display 6 articles per page
    sort_by = request.args.get('sort', 'newest')
    search_query = request.args.get('q', '')
    if search_query:
        articles_query = Article.query.filter(
            or_(
                Article.title.ilike(f'%{search_query}%'),
                Article.content_html.ilike(f'%{search_query}%')
            )
        )
    else:
        articles_query = Article.query
    
    # Sorting logic
    if sort_by == 'oldest':
        order_by = Article.date_published.asc()
    elif sort_by == 'title_asc':
        order_by = Article.title.asc()
    elif sort_by == 'title_desc':
        order_by = Article.title.desc()
    elif sort_by == 'updated':
        order_by = Article.last_updated.desc()
    else:  # Default to 'newest'
        order_by = Article.date_published.desc()

    pagination = articles_query.order_by(order_by).paginate(
        page=page, per_page=per_page, error_out=False
    )
    articles = pagination.items
    return render_template('articles.html', articles=articles, pagination=pagination, search_query=search_query, sort_by=sort_by, page_title="Strategy Articles")

@articles_bp.route('/tag/<string:tag_name>')
@login_required
def by_tag(tag_name):
    """Display articles filtered by a specific tag."""
    tag = Tag.query.filter_by(name=tag_name).first_or_404()
    page = request.args.get('page', 1, type=int)
    per_page = 6
    
    pagination = tag.articles.order_by(Article.date_published.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    articles = pagination.items
    return render_template('articles.html', articles=articles, pagination=pagination, page_title=f"Articles tagged with '{tag.name}'")

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
