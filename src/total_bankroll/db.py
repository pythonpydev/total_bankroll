import mysql.connector
from flask import g, current_app
from .currency import insert_initial_currency_data

def get_db():
    if "db" not in g:
        try:
            g.db = mysql.connector.connect(
                host=current_app.config['DB_HOST'],
                database=current_app.config['DB_NAME'],
                user=current_app.config['DB_USER'],
                password=current_app.config['DB_PASS']
            )
        except mysql.connector.errors.ProgrammingError as err:
            if err.errno == 1049: # ER_BAD_DB_ERROR (Database does not exist)
                # Connect to MySQL server without specifying a database
                conn_no_db = mysql.connector.connect(
                    host=current_app.config['DB_HOST'],
                    user=current_app.config['DB_USER'],
                    password=current_app.config['DB_PASS']
                )
                cursor_no_db = conn_no_db.cursor()
                cursor_no_db.execute(f"CREATE DATABASE IF NOT EXISTS {current_app.config['DB_NAME']}")
                conn_no_db.commit()
                cursor_no_db.close()
                conn_no_db.close()

                # Reconnect to the newly created database
                g.db = mysql.connector.connect(
                    host=current_app.config['DB_HOST'],
                    database=current_app.config['DB_NAME'],
                    user=current_app.config['DB_USER'],
                    password=current_app.config['DB_PASS']
                )
                # Initialize tables after creating the database
                _init_db_tables(g.db, current_app)
            else:
                raise err

    return g.db

def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def _init_db_tables(db_connection, app):
    cursor = db_connection.cursor()
    with app.open_resource('schema.sql') as f:
        sql_script = f.read().decode('utf8')
        for statement in sql_script.split(';'):
            if statement.strip():
                cursor.execute(statement)
    db_connection.commit()
    cursor.close()
    insert_initial_currency_data(db_connection)

def init_app(app):
    app.teardown_appcontext(close_db)
    # No need to add init_db_command to cli anymore

