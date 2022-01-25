from bson import ObjectId
from datetime import datetime
from flask import (
    Blueprint, current_app, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort
from ragstoriches.auth import login_required
from ragstoriches.db import get_db

bp = Blueprint('game_of_life', __name__)


@bp.route('/begin', methods=['GET','POST'])
@login_required
def begin():
    db = get_db()
    if request.method == 'POST':
        # TODO
        pass


    user_id = ObjectId(session['user_id'])
    query = {"user_id": user_id}
    find_character = db.character.find_one(query)
    if find_character is None:
        return redirect(url_for('game_of_life.create'))
    
    else:
        if session.get('character_id') is None:
            session['character_id'] = str(find_character['_id'])
    

    return render_template('game/begin.html')


@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    db = get_db()
    user_id = ObjectId(session['user_id'])
    query = {"user_id": user_id}
    find_character = db.character.find_one(query)

    error_message = None

    if find_character is not None:
        error_message = "You already created a character"
        flash(error_message)
        return redirect(url_for('game_of_life.begin'))


    if request.method == 'POST':


        character_name = request.form['name']
        character_funds = float(request.form['funds'])
        if character_name is None:
            error_message = "Character name is required"
        
        if character_funds < 0:
            error_message = "Please input a positive integer number"

        
        # default values for character_info
        character_info = {
            "name" : character_name,
            "funds" : character_funds,
            "progress": 0,
            "end" : False,
            "user_id": user_id,
            "created_at": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "updated_at": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        }
            

        character_id = db.character.insert_one(character_info).inserted_id
        session['character_id'] = str(character_id)
        success_message = "Character created!"
        flash(success_message)
        return redirect(url_for('game_of_life.begin'))

    if error_message is not None:
        flash(error_message)
    
    return render_template('game/create.html')


@bp.route('/update', methods=['GET', 'POST'])
@login_required
def update():
    db = get_db()
    character_id = ObjectId(session['character_id'])
    query = {"_id": character_id}
    find_character = db.character.find_one(query)
    error_message = None

    if find_character is None:
        error_message = "No character found"
        flash(error_message)
        return redirect(url_for('game_of_life.begin'))
    

    if request.method == 'POST':

        new_name = request.form['name']
        new_fund = float(request.form['funds'])

        if new_name is None:
            error_message = "Name cannot be empty"
        
        if new_fund < 0:
            error_message = "Please input a positive integer value"
        
        if error_message is None:

            # Update value for character_info
            character_info = {
                "name" : new_name,
                "funds" : new_fund,
                "updated_at": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            }


        query = {"_id": character_id}
        value = {"$set": character_info}
        db.character.update_one(query, value)
        success_message = "Character updated!"
        flash(success_message)
        return redirect(url_for('game_of_life.begin'))

    

    return render_template('game/update.html',character_info=find_character)



@bp.before_app_request
def load_character():
    character_id = session.get('character_id')

    if character_id is None:
        g.character = None
    
    else:
        db = get_db()
        the_object_id = ObjectId(character_id)
        query = {"_id": the_object_id}
        g.character= db.character.find_one(query)
        show_character = {
            "Name": g.character['name'],
            "Funds": g.character['funds']
        }
        setattr(g, 'show_character', show_character)