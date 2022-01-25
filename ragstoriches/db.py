'''
https://flask-pymongo.readthedocs.io/en/latest/
https://github.com/mongodb-developer/flask-pymongo-example/blob/main/mflix/db.py
https://www.mongodb.com/compatibility/setting-up-flask-with-mongodb

'''

from flask_pymongo import PyMongo
import click
from flask import current_app, g
from flask.cli import with_appcontext

def get_db():
    db = getattr(g, "db", None)
    if db is None:
        db = g.db = PyMongo(current_app).db
    
    return g.db

def close_db(e=None):
    # Remove connection
    g.pop('db', None)

def connect_db():
    db = get_db()
    if db is None:
        print("No connection")
    else:
        print("Connection success")

@click.command('connect-db')
@with_appcontext
def connect_db_command():
    click.echo(connect_db())


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(connect_db_command)
