from flask import g
import ragstoriches.database

def test_get_db(client):
    assert g.database is not None

def test_get_not_existing_user_by_email(client):
    assert ragstoriches.database.get_user_by_email("iamhandsome@example.com") is None

def test_get_existing_user_by_email(client):
    assert ragstoriches.database.get_user_by_email("test1@example.com") is not None

def test_check_user_with_correct_details(client):
    assert ragstoriches.database.check_user("test1", "test1@example.com", "123456") is not None

def test_check_user_with_wrong_password(client):
    assert ragstoriches.database.check_user("test1", "test1@example.com", "hello") == 2

def test_check_user_with_correct_password_but_wrong_details(client):
    assert ragstoriches.database.check_user("test2", "test1@example.com", "123456") == 0
    assert ragstoriches.database.check_user("test1", "test2@example.com", "123456") == 0

def test_add_user(client):
    assert ragstoriches.database.add_user("newtester", "newtester@example.com", "newtester666")