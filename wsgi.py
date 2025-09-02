import os
import sys

# add your project directory to the sys.path
project_home = '/home/pythonpydev/total_bankroll'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Change the current working directory so that .env is found by load_dotenv()
os.chdir(project_home)

# import flask app but need to call it "application" for WSGI to work
from src.total_bankroll import create_app
application = create_app()
