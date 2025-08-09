import psycopg2
from psycopg2.extras import DictCursor
from flask import g

DB_HOST = "localhost"
DB_NAME = "bankroll"
DB_USER = "efb"
DB_PASS = "post123!"

def get_db():
    if "db" not in g:
        g.db = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
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
