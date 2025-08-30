from flask_security import UserMixin
from .extensions import db
from datetime import datetime

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=True)  # Nullable for OAuth users
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login_at = db.Column(db.DateTime, nullable=True)
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)
    is_confirmed = db.Column(db.Boolean, default=False, nullable=False)
    confirmed_on = db.Column(db.DateTime, nullable=True)

    def get_id(self):
        return str(self.id)

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
    user = db.relationship('User', backref=db.backref('sites', lazy='dynamic'))

class Assets(db.Model):
    __tablename__ = 'assets'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('assets', lazy='dynamic'))

class Deposits(db.Model):
    __tablename__ = 'deposits'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    last_updated = db.Column(db.DateTime, nullable=False)
    currency = db.Column(db.String(255), nullable=False, default='Dollar')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('deposits', lazy='dynamic'))

class Drawings(db.Model):
    __tablename__ = 'drawings'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    last_updated = db.Column(db.DateTime, nullable=False)
    currency = db.Column(db.String(255), nullable=False, default='Dollar')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('drawings', lazy='dynamic'))

class SiteHistory(db.Model):
    __tablename__ = 'site_history'
    id = db.Column(db.Integer, primary_key=True)
    site_id = db.Column(db.Integer, db.ForeignKey('sites.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(255), nullable=False)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    site = db.relationship('Sites', backref=db.backref('history', lazy='dynamic'))
    user = db.relationship('User', backref=db.backref('site_history', lazy='dynamic'))

class AssetHistory(db.Model):
    __tablename__ = 'asset_history'
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(255), nullable=False)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    asset = db.relationship('Assets', backref=db.backref('history', lazy='dynamic'))
    user = db.relationship('User', backref=db.backref('asset_history', lazy='dynamic'))

class Currency(db.Model):
    __tablename__ = 'currency'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    rate = db.Column(db.Numeric(10, 6), nullable=False)
    code = db.Column(db.String(3), nullable=False)
    symbol = db.Column(db.String(5), nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CashStakes(db.Model):
    __tablename__ = 'cash_stakes'
    id = db.Column(db.Integer, primary_key=True)
    small_blind = db.Column(db.Numeric(10, 2), nullable=False)
    big_blind = db.Column(db.Numeric(10, 2), nullable=False)
    min_buy_in = db.Column(db.Numeric(10, 2), nullable=False)
    max_buy_in = db.Column(db.Numeric(10, 2), nullable=False)