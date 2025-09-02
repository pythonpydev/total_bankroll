
import os
os.environ['FLASK_ENV'] = 'production'

os.environ['SECRET_KEY'] = '98d204857f00202e3ce068ba68395611'
os.environ['SECURITY_PASSWORD_SALT'] = '51f67609a93551a032f59514e12567caa7ff2ac101bda48914d4d76601042327'

# Exchange Rate API Key (from exchangerate-api.com)
os.environ['EXCHANGE_RATE_API_KEY'] = "447d94e4f5ddcbc0c179a1fd"

os.environ['PROD_DB_HOST'] = 'pythonpydev.mysql.pythonanywhere-services.com'
os.environ['PROD_DB_NAME'] = 'pythonpydev$bankroll'
os.environ['PROD_DB_USER'] = 'pythonpydev'
os.environ['PROD_DB_PASS'] = 'f3gWoQe7X7BFCm'

# Email settings
os.environ['MAIL_SERVER'] = 'smtp.gmail.com'
os.environ['MAIL_PORT'] = '587'
os.environ['MAIL_USE_TLS'] = 'True'
os.environ['MAIL_USERNAME'] = 'pythonpydev1@gmail.com'
os.environ['MAIL_PASSWORD'] = 'pfav ftkn tdqz wwtr'

# Google OAuth Credentials
# https://console.cloud.google.com/auth/clients?inv=1&invt=Ab56WA&project=stable-course-469516-p8
os.environ['GOOGLE_CLIENT_ID']="930176693065-3ed24l13tfp29qa17a2au8hn06lqsaep.apps.googleusercontent.com"
os.environ['GOOGLE_CLIENT_SECRET']="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"


import sys

# add your project directory to the sys.path
project_home = '/home/pythonpydev/total_bankroll'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# import flask app but need to call it "application" for WSGI to work
from src.total_bankroll import create_app
application = create_app()
