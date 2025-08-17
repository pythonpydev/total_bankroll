import pymysql
from flask import g, current_app
from .currency import insert_initial_currency_data

def get_db():
    if "db" not in g:
        try:
            g.db = pymysql.connect(
                host=current_app.config['DB_HOST'],
                database=current_app.config['DB_NAME'],
                user=current_app.config['DB_USER'],
                password=current_app.config['DB_PASS'],
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=False
            )

            # Check if tables exist, if not initialize them
            cursor = g.db.cursor()
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            cursor.close()

            if not tables:  # No tables exist, initialize database
                _init_db_tables(g.db, current_app)

        except Exception as e:
            # If there's an error, make sure we don't leave a broken connection
            if hasattr(g, 'db') and g.db:
                try:
                    g.db.close()
                except:
                    pass
                g.pop('db', None)
            raise e
        except pymysql.err.OperationalError as err:
            if err.args[0] == 1049: # ER_BAD_DB_ERROR (Database does not exist)
                # Connect to MySQL server without specifying a database
                conn_no_db = pymysql.connect(
                    host=current_app.config['DB_HOST'],
                    user=current_app.config['DB_USER'],
                    password=current_app.config['DB_PASS'],
                    charset='utf8mb4'
                )
                cursor_no_db = conn_no_db.cursor()
                cursor_no_db.execute(f"CREATE DATABASE IF NOT EXISTS {current_app.config['DB_NAME']}")
                conn_no_db.commit()
                cursor_no_db.close()
                conn_no_db.close()

                # Reconnect to the newly created database
                g.db = pymysql.connect(
                    host=current_app.config['DB_HOST'],
                    database=current_app.config['DB_NAME'],
                    user=current_app.config['DB_USER'],
                    password=current_app.config['DB_PASS'],
                    charset='utf8mb4',
                    cursorclass=pymysql.cursors.DictCursor,
                    autocommit=False
                )
                # Initialize tables after creating the database
                _init_db_tables(g.db, current_app)
            else:
                raise err

    return g.db

def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        try:
            if not db._closed:
                db.close()
        except (AttributeError, Exception):
            # Connection was already closed or doesn't have _closed attribute
            pass

def _init_db_tables(db_connection, app):
    cursor = db_connection.cursor()
    try:
        with app.open_resource('schema.sql') as f:
            sql_script = f.read().decode('utf8')
            # Execute each statement separately
            statements = [stmt.strip() for stmt in sql_script.split(';') if stmt.strip()]
            for statement in statements:
                cursor.execute(statement)
        db_connection.commit()
        insert_initial_currency_data(db_connection)
    except Exception as e:
        db_connection.rollback()
        raise e
    finally:
        cursor.close()

def init_app(app):
    app.teardown_appcontext(close_db)
    # No need to add init_db_command to cli anymore