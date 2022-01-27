'''
https://flask-pymongo.readthedocs.io/en/latest/
https://github.com/mongodb-developer/flask-pymongo-example/blob/main/mflix/db.py
https://www.mongodb.com/compatibility/setting-up-flask-with-mongodb

'''

import bson
import click

from flask import current_app, g
from flask_pymongo import PyMongo
from flask.cli import with_appcontext
from werkzeug.local import LocalProxy
from werkzeug.security import generate_password_hash, check_password_hash

from pymongo.errors import DuplicateKeyError, OperationFailure
from bson.objectid import ObjectId
from bson.errors import InvalidId

from datetime import datetime

def get_db():
    db = getattr(g, "database", None)
    if db is None:
        db = g.database = PyMongo(current_app).db
    
    return db

# Use LocalProxy to read the global db instance with just `db`
db = LocalProxy(get_db)

def add_user(name, email, password):
    '''
    Insert a user into the user collection, with the following fields:
    -'name"
    -'password'
    -'email'
    -'created_at'

    name, password and email will be retrieved from register form
    
    Return the result of "db.user.insert_one(user)"
    '''

    user = {
        "name": name, 
        "email": email, 
        "password": generate_password_hash(password),
        "created_at": datetime.now(),
    }
    return db.user.insert_one(user)

def check_user(name, email, password):
    '''
    Check if the user exist in the user collection

    if exist return "db.user.find_one(details)" 
    if not exist, return 0
    if password is wrong, return 2
    '''
    details = {"name": name, "email": email}
    result = db.user.find_one(details)
    if result is None:
        # User does not exist
        return 0
    if check_password_hash(result['password'], password):
        return result
    else:
        # Password is incorrect
        return 2

def get_user_by_oid(user_oid):
    '''
    Retrieve user details from collection by their object id

    Return the user in python dictionary format
    '''
    return db.user.find_one({"_id": ObjectId(user_oid)})

def get_user_by_email(email):
    '''
    Retrieve user details from collection by their email

    return None if there is no user with the email given
    '''
    return db.user.find_one({"email": email})


# def close_db(e=None):
#     # Remove connection
#     g.pop('db', None)

# def connect_db():
#     db = get_db()
#     if db is None:
#         print("No connection")
#     else:
#         print("Connection success")

# @click.command('connect-db')
# @with_appcontext
# def connect_db_command():
#     click.echo(connect_db())


# def init_app(app):
#     app.teardown_appcontext(close_db)
#     app.cli.add_command(connect_db_command)
