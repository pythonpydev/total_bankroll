# test_db_connection.py
import pymysql

try:
    connection = pymysql.connect(
        host='pythonpydev.mysql.pythonanywhere-services.com',
        user='pythonpydev',
        password='f3gWoQe7X7BFCm',
        database='pythonpydev$bankroll'
    )
    print("Connection successful!")
    connection.close()
except pymysql.err.OperationalError as e:
    print(f"Connection failed: {e}")
