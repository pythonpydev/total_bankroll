# test_env.py
import os
from dotenv import load_dotenv

# Determine the base directory of the script
basedir = os.path.abspath(os.path.dirname(__file__))
# Construct the path to the .env file in /home/pythonpydev/total_bankroll
dotenv_path = os.path.join(basedir, '.env')  # .env is in the same directory as test_env.py
# Alternatively, use absolute path: dotenv_path = '/home/pythonpydev/total_bankroll/.env'

load_dotenv(dotenv_path=dotenv_path)

print(f".env path: {dotenv_path}")
print(f"DB_HOST_PROD: {os.getenv('DB_HOST_PROD')}")
print(f"DB_USER_PROD: {os.getenv('DB_USER_PROD')}")
print(f"DB_PASS_PROD: {os.getenv('DB_PASS_PROD')}")
print(f"DB_NAME_PROD: {os.getenv('DB_NAME_PROD')}")
