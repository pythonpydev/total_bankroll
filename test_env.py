# test_env.py
import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
dotenv_path = os.path.join(basedir, '..', '..', '.env')
print(f"Current working directory: {os.getcwd()}")
print(f"Attempting to load .env from: {dotenv_path}")
print(f".env file exists: {os.path.exists(dotenv_path)}")
if os.path.exists(dotenv_path):
    with open(dotenv_path, 'r', encoding='utf-8') as f:
        print(f".env contents:\n{f.read()}")
else:
    print(f"Error: .env file not found at {dotenv_path}")
load_dotenv(dotenv_path=dotenv_path, override=True)
print(f"After load_dotenv - DB_HOST_PROD: {os.getenv('DB_HOST_PROD')}")
print(f"After load_dotenv - DB_USER_PROD: {os.getenv('DB_USER_PROD')}")
print(f"After load_dotenv - DB_PASS_PROD: {os.getenv('DB_PASS_PROD')}")
print(f"After load_dotenv - DB_NAME_PROD: {os.getenv('DB_NAME_PROD')}")
