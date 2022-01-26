from crypt import methods
from distutils.log import error
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
        character_id = ObjectId(session['character_id'])
        user_id = ObjectId(session['user_id'])
        query = {"_id": character_id, "user_id": user_id}
        value = {"$set": {"progress": 1}}
        db.character.update_one(query, value)
        find_character= db.character.find_one(query)
        return redirect(url_for('game_of_life.scenarios', scenario=find_character['progress']))


    user_id = ObjectId(session['user_id'])
    query = {"user_id": user_id}
    find_character = db.character.find_one(query)
    if find_character is None:
        return redirect(url_for('game_of_life.create'))
    
    else:
        if session.get('character_id') is None:
            session['character_id'] = str(find_character['_id'])
    

    return render_template('game/begin.html')

@bp.route('/scenarios/<int:scenario>', methods=['GET','POST'])
@login_required
def scenarios(scenario):
    db = get_db()
    character_id = ObjectId(session['character_id'])
    user_id = ObjectId(session['user_id'])
    query = {"_id": character_id, "user_id": user_id}
    character_info = db.character.find_one(query)
    if character_info is None:
        error_message = "Character not found"
        flash(error_message, 'error')
        return redirect(url_for('game_of_life.begin'))
    
    elif character_info['progress'] == 0:
        error_message = "Please click the play button to proceed"
        flash(error_message, 'error')
        return redirect(url_for('game_of_life.begin'))

    elif character_info['progress'] != scenario:
        flash("Redirected back", 'error')
        return redirect(url_for('game_of_life.scenarios', scenario=character_info['progress']))

    
    if request.method == 'POST':
        choice = request.form['choice']
        if choice is None:
            error_message = "Please make a decision"
            flash(error_message, 'error')
            return redirect(url_for('scenarios', scenario=scenario))

        current_funds = character_info['funds']
        if scenario == 1:
            if choice == 'yes':
                new_funds = current_funds + 600
                value = {"$set": {"funds": new_funds, "progress": 2}}
                db.character.update_one(query, value)
                updated_character_info = db.character.find_one(query)
                return redirect(url_for('game_of_life.scenarios',scenario=updated_character_info['progress']))
            elif choice == 'no':
                value = {"$set": {"progress": 2}}
                db.character.update_one(query, value)
                updated_character_info = db.character.find_one(query)
                return redirect(url_for('game_of_life.scenarios',scenario=updated_character_info['progress']))
            else:
                error_message = "Invalid choice"
                flash(error_message, 'error')
                return redirect(url_for('game_of_life.scenarios',scenario=scenario))
        
        if scenario == 2:
            if choice == 'fund':
                new_funds = current_funds + 200
                value = {"$set": {"funds": new_funds, "progress": 3}}
                db.character.update_one(query, value)
                updated_character_info = db.character.find_one(query)
                return redirect(url_for('game_of_life.scenarios',scenario=updated_character_info['progress']))
            elif choice == 'course':
                new_funds = current_funds - 200
                value = {"$set": {"funds": new_funds, "progress": 3}}
                db.character.update_one(query, value)
                updated_character_info = db.character.find_one(query)
                return redirect(url_for('game_of_life.scenarios',scenario=updated_character_info['progress']))
            else:
                error_message = "Invalid choice"
                flash(error_message, 'error')
                return redirect(url_for('game_of_life.scenarios',scenario=scenario))
        
        if scenario == 3:
            pass




    return render_template('game/scenario.html', scenario=character_info['progress'], character_info=character_info)


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
        flash(error_message, 'error')
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
        flash(success_message, 'success')
        return redirect(url_for('game_of_life.begin'))

    if error_message is not None:
        flash(error_message, 'error')
    
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
        flash(error_message, 'error')
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
        flash(success_message, 'success')
        return redirect(url_for('game_of_life.begin'))

    

    return render_template('game/update.html',character_info=find_character)



@bp.before_app_request
def load_character():
    character_id = session.get('character_id')
    user_id = session.get('user_id')

    if character_id is None and user_id is None:
        g.character = None
    
    elif user_id is not None:
        db = get_db()
        the_user_object_id = ObjectId(user_id)
        result = db.character.find_one({"user_id": the_user_object_id})
        if result is not None:
            g.character = result
    
    elif character_id is not None:
        db = get_db()
        the_character_object_id = ObjectId(character_id)
        g.character = db.character.find_one({"_id": the_character_object_id})

    if g.character:
        show_character = {
            "Name": g.character['name'],
            "Funds": g.character['funds']
        }
        setattr(g, 'show_character', show_character)