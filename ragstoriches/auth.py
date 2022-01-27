import functools

from flask import (
    Blueprint, current_app, flash, g, redirect, render_template, request, session, url_for
)

import ragstoriches.database as database

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':
        name = request.form['username']
        email = request.form['email']
        password = request.form['password']
        error_message = None
        success_message = None

        if not name:
            error_message = "User name is required"
        elif not password:
            error_message = "Password is required"
        elif not email:
            error_message = "Email is required"
        
        if error_message is None:
            exist = database.get_user_by_email(email)
            if exist is None:
                new_user = database.add_user(name, email, password)
                session['user_id'] = str(new_user.inserted_id)
                success_message = "Registration success!"
                flash(success_message, 'success')
                return redirect(url_for("auth.login"))

            else:
                error_message = "This account has already been registered"
                flash(error_message, 'error')
                return redirect(url_for('auth.register'))
        
        if error_message is not None:
            flash(error_message, 'error')
    
    return render_template('auth/register.html')

@bp.route('/login', methods=["GET","POST"])
def login():
    if getattr(g,'user',None) is not None:
        flash("You were logged in!", 'success')
        return redirect(url_for("index"))
        
    if request.method == 'POST':
        name = request.form['username']
        password = request.form['password']
        email = request.form['email']
        
        error_message = None
        success_message = None

        result = database.check_user(name, email, password)

        if result == 2 or result == 0: # incorrect password or user does not exist
            error_message = "Incorrect details"
            flash(error_message, 'error')
            return redirect(url_for('auth.login'))
        
        else:
            session.clear()
            session['user_id'] = str(result['_id'])
            success_message = "Login success!"
            flash(success_message, 'success')
            return redirect(url_for('game_of_life.begin'))

    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    
    else:
        g.user = database.get_user_by_oid(user_id)

@bp.route('/logout')
def logout():
    session.clear()
    success_message = "You are logged out"
    flash(success_message, 'success')
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_views(**kwargs):
        if getattr(g, 'user', None) is None:
            return redirect(url_for('auth.login'))
        
        return view(**kwargs)
    return wrapped_views