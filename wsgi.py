import sys
import os

# Add project directory to Python path
project_home = '/home/pythonpydev/total_bankroll/src'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set Flask environment to production
os.environ['FLASK_ENV'] = 'production'

# Import the Flask application
from total_bankroll.app import app as application