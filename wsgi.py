import os
os.environ['SECRET_KEY'] = '98d204857f00202e3ce068ba68395611'

# Exchange Rate API Key (from exchangerate-api.com)
EXCHANGE_RATE_API_KEY="447d94e4f5ddcbc0c179a1fd"

os.environ['DB_HOST'] = 'pythonpydev.mysql.pythonanywhere-services.com'
os.environ['DB_NAME'] = 'pythonpydev$bankroll'
os.environ['DB_USER'] = 'pythonpydev'
os.environ['DB_PASS'] = 'f3gWoQe7X7BFCm'

# Email settings
os.environ['MAIL_SERVER'] = 'smtp.gmail.com'
os.environ['MAIL_PORT'] = '587'
os.environ['MAIL_USE_TLS'] = 'True'
os.environ['MAIL_USERNAME'] = 'pythonpydev1@gmail.com'
os.environ['MAIL_PASSWORD'] = 'pfav ftkn tdqz wwtr'
  # <-- PASTE THE APP PASSWORD HERE
os.environ['MAIL_DEFAULT_SENDER'] = 'pythonpydev1@gmail.com'



import sys

# add your project directory to the sys.path
project_home = '/home/pythonpydev/total_bankroll'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# import flask app but need to call it "application" for WSGI to work
from src.total_bankroll import create_app
application = create_app()
