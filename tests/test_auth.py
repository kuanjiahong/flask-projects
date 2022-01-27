from flask import g, session


def test_register_get_method(client):
    assert client.get('/auth/register').status_code == 200



def test_register_with_new_user(client):
    response = client.post(
        '/auth/register', 
        data={'username':'a', 'email':'a', 'password':'a'}
    )
    assert response.headers['Location'] == 'http://localhost/auth/login'
    assert response.status_code == 302

def test_register_with_existing_user(client):
    client.post(
        '/auth/register',
        data={'username':'a', 'email':'test1@example.com', 'password':'a'}
    )
    response = client.post(
        '/auth/register',
        data={'username':'a', 'email':'test1@example.com', 'password':'a'}
    )

    assert response.headers['Location'] == 'http://localhost/auth/register' #redirect back to registers
    assert response.status_code == 302 # redirected

def test_login(client):
    assert client.get('/auth/login').status_code == 200


def test_login_with_registered_user(client):

    response = client.post(
        '/auth/login',
        data={'username':'test1', 'email':'test1@example.com', 'password':'123456'},
        follow_redirects=True
    )

    assert session.get('user_id') is not None
    assert b"Login success!" in  response.data

def test_login_with_registered_user_with_incorrect_details(client):
    # wrong username
    response = client.post( 
        '/auth/login',
        data={'username':'test2', 'email':'test1@example.com', 'password':'123456'},
        follow_redirects=True
    ) 

    assert session.get('user_id') is None
    assert b"Incorrect details" in response.data


    # wrong email
    response = client.post( 
        '/auth/login',
        data={'username':'test1', 'email':'test2@example.com', 'password':'123456'},
        follow_redirects=True
    ) 

    assert session.get('user_id') is None
    assert b"Incorrect details" in response.data


    # wrong password
    response = client.post( 
        '/auth/login',
        data={'username':'test1', 'email':'test2@example.com', 'password':'helloworld'},
        follow_redirects=True
    ) 

    assert session.get('user_id') is None
    assert b"Incorrect details" in response.data


def test_logout(client):
    client.get('auth/logout')
    assert session.get('user_id') is None