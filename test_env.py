# test_env.py
import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
dotenv_path = os.path.join(basedir, '..', '..', '.env')
load_dotenv(dotenv_path=dotenv_path)

print(f".env path: {dotenv_path}")
print(f"DB_HOST_PROD: {os.getenv('DB_HOST_PROD')}")
print(f"DB_USER_PROD: {os.getenv('DB_USER_PROD')}")
print(f"DB_PASS_PROD: {os.getenv('DB_PASS_PROD')}")
print(f"DB_NAME_PROD: {os.getenv('DB_NAME_PROD')}")
