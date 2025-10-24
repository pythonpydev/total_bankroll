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
    title = db.Column(db.String(200), nullable=False, unique=True)
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