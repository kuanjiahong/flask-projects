from crypt import methods
from distutils.log import error
from bson import ObjectId
from datetime import datetime
from flask import (
    Blueprint, current_app, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort
from ragstoriches.auth import login, login_required
from ragstoriches.database import get_db

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

        plus = False
        minus = False
        money = 0
        investment_value = character_info['insurance']
        insurance_value = character_info['investment']
        current_funds = character_info['funds']

        if scenario == 1:
            money = 600
            if choice == 'yes':
                plus = True
                current_funds += money
            elif choice == 'no':
                minus = True
                current_funds -= money
            else:
                error_message = "Invalid choice"
                flash(error_message, 'error')
                return redirect(url_for('game_of_life.scenarios',scenario=scenario))
        
        if scenario == 2:
            money = 200
            if choice == 'fund':
                plus = True
                current_funds += money
            elif choice == 'course':
                minus = True
                current_funds -= money
            else:
                error_message = "Invalid choice"
                flash(error_message, 'error')
                return redirect(url_for('game_of_life.scenarios',scenario=scenario))
        
        if scenario == 3:
            minus = True
            if choice == 'branded':
                money = 500
                current_funds -= money
            elif choice == 'non-branded':
                money = 200
                current_funds -= money
            else:
                error_message = "Invalid choice"
                flash(error_message, 'error')
                return redirect(url_for('game_of_life.scenarios',scenario=scenario))

        if scenario == 4:
            plus = True
            if choice == 'promotion':
                money = 1000
                current_funds += money
            elif choice == 'no-promotion':
                money = 2000
                current_funds += money
            else:
                error_message = "Invalid choice"
                flash(error_message, 'error')
                return redirect(url_for('game_of_life.scenarios',scenario=scenario))
        
        if scenario == 5:
            minus = True
            if choice == 'posh':
                money = 500 + 100
                current_funds -= money
            elif choice == 'cheaper':
                money = 300 + 100
                current_funds -+ money
            else:
                error_message = "Invalid choice"
                flash(error_message, 'error')
                return redirect(url_for('game_of_life.scenarios',scenario=scenario))

            current_funds = 10000 # the next scenario (6) will say that we have 10000 left

        if scenario == 6:
            minus = True
            money = 1000
            if choice == 'nasdaq':
                current_funds -= money
                investment_value += money
            elif choice == 'insurance':
                current_funds -= money
                insurance_value += money
            else:
                error_message = "Invalid choice"
                flash(error_message, 'error')
                return redirect(url_for('game_of_life.scenarios',scenario=scenario))
            
            current_funds = 12000 # the next scenario which is 7 will say that we have 12000 left
        
        if scenario == 7:
            if choice == 'insurance':
                minus = True
                money = 1000
                current_funds -= money
                insurance_value += money
            elif choice == 'rent':
                minus = True
                money = 1000
                current_funds -= money
            elif choice == 'car':
                minus = True
                money = 90000
                current_funds -= money
            elif choice == 'public-transport':
                plus = True
                money = 0
                current_funds += money
            else:
                error_message = "Invalid choice"
                flash(error_message, 'error')
                return redirect(url_for('game_of_life.scenarios',scenario=scenario))

            current_funds = 6000 # scenario 8 will give us 6000 cash surplus

        if scenario == 8: # the last question
            if choice == 'savings':
                pass
            elif choice == 'fixed-deposit':
                pass
            else:
                error_message = "Invalid choice"
                flash(error_message, 'error')
                return redirect(url_for('game_of_life.scenarios',scenario=scenario))

            value = {
                "$set": {
                    "funds": current_funds,   
                    "end": True
                }
            }

            db.character.update_one(query, value)

            return redirect(url_for('game_of_life.end'))



        value = {
            "$set": {
                "funds": current_funds, 
                "progress": scenario + 1, 
                "investment": investment_value, 
                "insurance": insurance_value
                }
        }

        db.character.update_one(query, value)

        updated_character_info = db.character.find_one(query)

        if plus == True:
            plus_message=f"You gained ${money}"
            flash(plus_message, 'plus')
        elif minus == True:
            minus_message = f'You lost ${money}'
            flash(minus_message, 'minus')
        
        return redirect(url_for('game_of_life.scenarios',scenario=updated_character_info['progress']))
        

    return render_template('game/scenario.html', scenario=character_info['progress'], character_info=character_info)


@bp.route('/end', methods=['GET','POST'])
@login_required
def end():

    db = get_db()
    character_id = ObjectId(session['character_id'])
    user_id = ObjectId(session['user_id'])
    query = {"_id": character_id, "user_id": user_id}
    character_info = db.character.find_one(query)

    if character_info is None:
        error_message = "Character not found"
        flash(error_message, 'error')
        return redirect(url_for('game_of_life.begin'))
    
    if character_info['end'] == False:
        error_message = "Your game hasn't ended yet"
        flash(error_message, 'error')
        return redirect(url_for('game_of_life.begin'))
    
    if request.method == 'POST':
        choice = request.form['choice']
        if choice is None:
            error_message = "Invalid input"
            flash(error_message, 'error')
            return redirect(url_for('game_of_life.end'))
        
        if choice == 'restart':
            db.character.delete_one(query)
            success_message = "Game restarted"
            flash(success_message, 'success')
            return redirect(url_for('game_of_life.begin'))

    display_result = {
        "Name": character_info['name'],
        "Available Funds": character_info['funds'],
        "Insurance": character_info['insurance'],
        "Investment value": character_info['investment']
    }

    return render_template('game/end.html', result=display_result)
    


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

    if getattr(g, 'character', None) is not None:
        show_character = {
            "Name": g.character['name'],
            "Funds": g.character['funds']
        }
        setattr(g, 'show_character', show_character)