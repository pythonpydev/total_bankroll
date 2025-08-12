import psycopg2
from psycopg2.extras import DictCursor
from flask import g, current_app
import os

def get_db():
    if "db" not in g:
        g.db = psycopg2.connect(
            host=current_app.config['DB_HOST'],
            database=current_app.config['DB_NAME'],
            user=current_app.config['DB_USER'],
            password=current_app.config['DB_PASS'],
            cursor_factory=DictCursor
        )
    return g.db

def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_db(app):
    with app.app_context():
        conn = get_db()
        cur = conn.cursor()
        print(f"Initializing database: {DB_NAME} on {DB_HOST}")
        with app.open_resource("schema_postgres.sql", mode="r") as f:
            sql_statements = f.read().split(';')
            for statement in sql_statements:
                if statement.strip():
                    cur.execute(statement)
        conn.commit()
        cur.close()
        conn.close()
        print("Database initialization complete.")
