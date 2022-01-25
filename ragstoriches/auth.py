import functools

from bson import ObjectId

from flask import (
    Blueprint, current_app, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from ragstoriches.db import get_db

import datetime

bp = Blueprint('auth', __name__, url_prefix='/auth')

user_info = {
    "username": "",
    "email": "",
    "password": "",
    "created_at": "",

}

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if g.user:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        db = get_db()
        error_message = None
        success_message = None

        if not username:
            error_message = "Username is required"
        elif not password:
            error_message = "Password is required"
        elif not email:
            error_message = "Email is required"
        
        if error_message is None:
            user_info['username'] = username
            user_info['email'] = email
            user_info['password'] = generate_password_hash(password)
            user_info['created_at'] = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

            query = {"email": email}
            result = db.user.find_one(query)
            current_app.logger.debug(result)
            if result is None:
                db.user.insert_one(user_info)
                success_message = "Registration success!"
                flash(success_message)
                return redirect(url_for("auth.login"))

            else:
                error_message = "This account has already been registered"
        
        
        if error_message is not None:
            flash(error_message)
    
    
    return render_template('auth/register.html')

@bp.route('/login', methods=["GET","POST"])
def login():
    if g.user:
        return redirect(url_for("index"))
        
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        db = get_db()
        error_message = None
        success_message = None
        query = {'username': username,'email': email}
        user = db.user.find_one(query)
        if user is None:
            error_message = "Incorrect details"
        elif not check_password_hash(user['password'], password):
            error_message = "Incorrect details"
        
        if error_message is None:
            session.clear()
            session['user_id'] = str(user['_id'])
            success_message = "Login success!"
            flash(success_message)
            return redirect(url_for('game_of_life.begin'))
        
        if error_message is not None:
            flash(error_message)
    
    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    
    else:
        db = get_db()
        the_user_object_id = ObjectId(user_id)
        g.user = db.user.find_one({"_id": the_user_object_id})

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_views(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        
        return view(**kwargs)
    return wrapped_views