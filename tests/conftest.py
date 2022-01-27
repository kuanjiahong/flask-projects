import pytest
from flask import g
from ragstoriches import create_app
import ragstoriches.database
from werkzeug.security import generate_password_hash

from datetime import datetime

random_users = [
    {"name": "test1", "email": "test1@example.com", "password": generate_password_hash("123456"), "created_at": datetime.now() },
    {"name": "test2", "email": "test2@example.com", "password": generate_password_hash("helloworld"), "created_at": datetime.now()},
]


@pytest.fixture
def client():
    app = create_app({"TESTING":True})

    with app.test_client() as c:
        with app.app_context():
            db = ragstoriches.database.get_db()
            db.user.insert_many(random_users)
            yield c
            db.user.delete_many({})