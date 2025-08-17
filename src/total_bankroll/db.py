import mysql.connector
from flask import g, current_app
import click
from flask.cli import with_appcontext

def get_db():
    if "db" not in g:
        g.db = mysql.connector.connect(
            host=current_app.config['DB_HOST'],
            database=current_app.config['DB_NAME'],
            user=current_app.config['DB_USER'],
            password=current_app.config['DB_PASS']
        )
    return g.db

def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    cursor = db.cursor()
    with current_app.open_resource('schema.sql') as f:
        sql_script = f.read().decode('utf8')
        for statement in sql_script.split(';'):
            if statement.strip():
                cursor.execute(statement)
    db.commit()
    close_db()

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

