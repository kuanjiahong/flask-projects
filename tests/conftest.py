import pytest
from flask import g
from ragstoriches import create_app
import ragstoriches.database
from werkzeug.security import generate_password_hash

from datetime import datetime

random_user =  {
    "name": "test1", 
    "email": "test1@example.com", 
    "password": generate_password_hash("123456"), 
    "progress": 0,
    "created_at": datetime.now(),
    "last_modified": datetime.now()
    }



@pytest.fixture
def client():
    app = create_app({"TESTING":True})

    with app.test_client() as c:
        with app.app_context():
            db = ragstoriches.database.get_db()
            g.oid = str(db.user.insert_one(random_user).inserted_id)
            yield c
            db.user.delete_many({})