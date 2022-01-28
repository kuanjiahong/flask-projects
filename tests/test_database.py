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

def test_get_user_by_oid(client):
    assert ragstoriches.database.get_user_by_oid(g.oid) is not None

def test_add_character(client):
    assert ragstoriches.database.add_character(g.oid, "John Cena", 1000) is True

def test_update_progress(client):
    assert ragstoriches.database.update_progress(g.oid) is True

    result = ragstoriches.database.get_user_by_oid(g.oid)
    assert result['progress'] > 0

def test_update_character_fund_and_progress(client):
    ragstoriches.database.add_character(g.oid, "John Cena", 1000)
    assert ragstoriches.database.update_character_fund_and_progress(g.oid, 2000) is True   
    result = ragstoriches.database.get_user_by_oid(g.oid)
    assert result['character']['name'] == "John Cena"
    assert result['character']['funds'] == 2000
    assert result['progress'] == 1

def test_update_end(client):
    ragstoriches.database.add_character(g.oid, "John Cena", 1000)
    assert ragstoriches.database.update_end(g.oid) is True
    result = ragstoriches.database.get_user_by_oid(g.oid)
    assert result['end'] == True

def test_delete_character(client):
    ragstoriches.database.add_character(g.oid, "John Cena", 1000)
    assert ragstoriches.database.delete_character(g.oid) is True
    result = ragstoriches.database.get_user_by_oid(g.oid)
    assert result.get('character') is None