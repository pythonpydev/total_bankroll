"""Web entry point for total_bankroll."""

import os
import os
from flask import Flask
from dotenv import load_dotenv
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin
from flask_sqlalchemy import SQLAlchemy
from total_bankroll.config import config

# Load environment variables from .env file
load_dotenv()

# Get the absolute path to the directory containing app.py
basedir = os.path.abspath(os.path.dirname(__file__))

# App initialization
app = Flask(__name__, template_folder=os.path.join(basedir, 'templates'))
app.config.from_object(config[os.getenv('FLASK_ENV', 'default')])

# Construct the database URI from environment variables
db_user = os.getenv('DB_USER', 'efb')
db_pass = os.getenv('DB_PASS', 'post123!')
db_host = os.getenv('DB_HOST', 'localhost')
db_name = os.getenv('DB_NAME', 'bankroll')
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_pass}@{db_host}/{db_name}'
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SECURITY_PASSWORD_SALT'] = os.getenv('SECURITY_PASSWORD_SALT')
app.config['SESSION_PROTECTION'] = 'strong' # Add this line


db = SQLAlchemy(app)

class User(db.Model, UserMixin):
    __tablename__ = 'users' # Explicitly set table name
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column('password_hash', db.String(255), nullable=False)
    active = db.Column(db.Boolean, default=True)
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    last_login_at = db.Column(db.DateTime)

    def get_id(self):
        return str(self.id) # Ensure ID is returned as a string

user_datastore = SQLAlchemyUserDatastore(db, User, None)
app.config['SECURITY_URL_PREFIX'] = "/security"
app.config['SECURITY_LOGIN_URL'] = "/security/login"
app.config['SECURITY_REGISTER_URL'] = "/security/register"
security = Security(app, user_datastore)

# Explicitly set Flask-Login's user_loader to Flask-Security's get_user method
# This might be redundant but ensures it's set if there's a conflict
from flask_login import LoginManager # Ensure this is imported if not already
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    print(f"load_user called with user_id: {user_id} (type: {type(user_id)})")
    if user_id is None or user_id == 'None':
        print("user_id is None or 'None', returning None")
        return None
    try:
        return db.session.get(User, int(user_id))
    except ValueError as e:
        print(f"Error loading user: {e}")
        return None

# Register Blueprints
from .routes.home import home_bp
from .routes.poker_sites import poker_sites_bp
from .routes.assets import assets_bp
from .routes.withdrawal import withdrawal_bp
from .routes.deposit import deposit_bp
from .routes.add_deposit import add_deposit_bp
from .routes.add_withdrawal import add_withdrawal_bp
from .routes.settings import settings_bp
from .routes.currency_update import currency_update_bp
from .routes.charts import charts_bp
from .routes.auth import auth_bp
from .routes.about import about_bp

app.register_blueprint(home_bp)
app.register_blueprint(poker_sites_bp)
app.register_blueprint(assets_bp)
app.register_blueprint(withdrawal_bp)
app.register_blueprint(deposit_bp)
app.register_blueprint(add_deposit_bp)
app.register_blueprint(add_withdrawal_bp)
app.register_blueprint(settings_bp)
app.register_blueprint(currency_update_bp)
app.register_blueprint(charts_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(about_bp)

if __name__ == "__main__":
    app.run(debug=True, port=5001)