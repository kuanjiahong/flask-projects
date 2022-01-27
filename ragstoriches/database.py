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
        "progress": 0,
        "end": False,
        "created_at": datetime.now(),
        "last_modified": datetime.now()
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


def add_character(user_id, character_name, funds):
    '''
    Update a character into the user collection

    Return True upon success

    else return error message
    '''
    query = {"_id": ObjectId(user_id)}
    set_value = { 
        "last_modified": datetime.now(),
        "character":{ # this is a nested/embedded document
            "name": character_name, 
            "funds": funds, 
        }
    }
    
    try:
        db.user.update_one(query, {"$set": set_value})
    except Exception as e:
        return e
    
    return True


def update_progress(user_id):
    '''
    Increment user progress by one

    If success, return True
    else, return error message
    '''
    query = {"_id": ObjectId(user_id)}
    inc_value = {"progress": 1}
    try:
        db.user.update_one(query, {"$inc": inc_value})
    except Exception as e:
        return e

    return True

def update_character_fund_and_progress(user_id, new_value):
    '''
    Update character fund to the new_value

    if success, return True

    else return error message
    '''
    query = {"_id": ObjectId(user_id)}
    set_value = {'character.funds': new_value}
    inc_value = {'progress': 1} # increase by one
    try:
        db.user.update_one(query, {"$set": set_value, "$inc": inc_value})
        return True
    except Exception as e:
        return e
    
def update_end(user_id):
    '''
    Mark the game as ended for the user

    if success, return True
    else return error message
    '''
    query = {"_id": ObjectId(user_id)}
    set_value = {"end": True}
    try:
        db.user.update_one(query, {"$set": set_value})
        return True
    except Exception as e:
        return e

def delete_character(user_id):
    '''
    Delete the "character" field and set user progress to 0 and also set "end" to False

    if success return True
    else return error message
    '''

    query = {"_id": ObjectId(user_id)}
    unset_value = {"character": ""}
    set_value = {"progress": 0, "end": False}
    try:
        db.user.update_one(query, {"$unset": unset_value, "$set": set_value})
        return True
    except Exception as e:
        return e