import pymysql, pymysql.cursors
from flask import g, current_app
from .currency import insert_initial_currency_data
from .extensions import db
from .models import Currency

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



def init_app(app):
    app.teardown_appcontext(close_db)
    db.init_app(app) # Initialize SQLAlchemy with the app
    with app.app_context():
        print("init_app called, app context active.")
        db.create_all() # Create all tables defined in SQLAlchemy models
        if db.session.query(Currency).first() is None:
            print("Currency table is empty in db.py. Calling insert_initial_currency_data().")
            insert_initial_currency_data()