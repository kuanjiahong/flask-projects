import pytest
from flask import g, current_app
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash
from ragstoriches import create_app
import ragstoriches.database

import bson
from datetime import datetime

random_users = [
    {"name": "test1", "email": "test1@example.com", "password": generate_password_hash("123456"), "created_at": datetime.now() },
    {"name": "test2", "email": "test2@example.com", "password": generate_password_hash("helloworld"), "created_at": datetime.now()},
]


@pytest.fixture
def check_database_app():
    app = create_app(
        {
            'TESTING': True, 
            'MONGO_URI': "mongodb+srv://jiahongk:thisisformongodb@cluster0.xitlo.mongodb.net/test_ragstoriches?retryWrites=true&w=majority"
        }
    )
    with app.app_context():
        db = ragstoriches.database.get_db()
        db.user.insert_many(random_users)

        yield app
        db.user.delete_many({})

    

def test_get_db(check_database_app):
    assert g.database is not None

def test_get_not_existing_user_by_email(check_database_app):
    assert ragstoriches.database.get_user_by_email("iamhandsome@example.com") is None

def test_get_existing_user_by_email(check_database_app):
    assert ragstoriches.database.get_user_by_email("test1@example.com") is not None

def test_check_user_with_correct_details(check_database_app):
    assert ragstoriches.database.check_user("test1", "test1@example.com", "123456") is not None

def test_check_user_with_wrong_password(check_database_app):
    assert ragstoriches.database.check_user("test1", "test1@example.com", "hello") == 2

def test_check_user_with_correct_password_but_wrong_details(check_database_app):
    assert ragstoriches.database.check_user("test2", "test1@example.com", "123456") == 0
    assert ragstoriches.database.check_user("test1", "test2@example.com", "123456") == 0

def test_add_user(check_database_app):
    assert ragstoriches.database.add_user("newtester", "newtester@example.com", "newtester666")