from flask import (
    Blueprint, current_app, flash, g, redirect, render_template, request, url_for, session
)

from ragstoriches.auth import login_required
import ragstoriches.database as database


bp = Blueprint('game_of_life', __name__)


@bp.route('/begin', methods=['GET','POST'])
@login_required
def begin():
    if request.method == 'POST':
        result = database.update_progress(session['user_id'])
        if result == True:
            return redirect(url_for('game_of_life.scenarios', scenario=1))
        else:
            error_message = "Something went wrong :(("
            flash(error_message, 'error')
            return redirect(url_for('game_of_life.begin'))

    if not g.user.get('character'):
        return redirect(url_for('game_of_life.create'))

    return render_template('game/begin.html')

def calculate(to_minus, to_plus, curr_fund, m):
    '''
    m stands for money

    curr_funds stand for current_funds

    If to_minus is True, return curr_fund - m

    else if to_plus is True, return curr_fund + m

    Please make sure the parameter are at the corret place
    '''
    if to_minus and to_plus:
        return "Both to_minus and to_plus are True value"

    if to_minus == True:
        return curr_fund - m
    
    if to_plus == True:
        return curr_fund + m

@bp.route('/scenarios/<int:scenario>', methods=['GET','POST'])
@login_required
def scenarios(scenario):
    if request.method == 'POST':

        choice = request.form['choice']

        if choice is None:
            error_message = "Please make a decision"
            flash(error_message, 'error')
            return redirect(url_for('game_of_life.scenarios', scenario=scenario))
        
        plus = False # positive alert if True
        minus = False # negative alert if True
        current_funds = g.user['character']['funds']
        money = -999999
        error_message = None
        last_scenario = 3 # change this accordingly

        # To be implemented - Awaiting future features
        investment_value = False
        insurance_value = False
        loan_value = False

        if scenario == 1:
            money = 600
            if choice == 'yes':
                plus = True
            elif choice == 'no':
                minus = True
            else:
                error_message = "Invalid choice"
        elif scenario == 2:
            money = 200
            if choice == "fund":
                plus = True
            elif choice == "course":
                minus = True
            else:
                error_message = "Invalid choice"
        elif scenario == 3:
            minus = True
            if choice == 'branded':
                money = 500
            elif choice == 'non-branded':
                money = 200
            else:
                error_message = "Invalid choice"
            
        
        if error_message is not None: # if error message exist
            flash(error_message, 'error')
            return redirect(url_for('game_of_life.scenarios', scenario=scenario))

        # Double check for potential bug
        if money == -999999: # log error message
            current_app.logger.error(f"Fail to change money value, money value is still {money}")
            error_message = "Something went wrong :((("
            flash(error_message, 'error')
            return redirect(url_for('game_of_life.scenarios', scenario=scenario))
        
        # the calculation
        outcome = calculate(minus, plus, current_funds, money)

        # Check if the calculation produce valid input
        if isinstance(outcome, str): # log error message
            current_app.logger.error(outcome)
            error_message = "Something went wrong :((("
            flash(error_message, 'error')
            return redirect(url_for('game_of_life.scenarios', scenario=scenario))

    
        new_funds = outcome

        # only update if different value
        if new_funds != current_funds: 
            result = database.update_character_fund_and_progress(session['user_id'], new_funds)
            if result != True:
                current_app.logger.error(result)
                error_message = "Something went wrong :((("
                flash(error_message, 'error')
                return redirect(url_for('game_of_life.scenarios', scenario=scenario))
        
        
        # Flash message
        if plus == True:
            plus_message = f"You gained ${money}"
            flash(plus_message, 'plus')
        elif minus == True:
            minus_message = f"You lost ${money}"
            flash(minus_message, 'minus')
        
        if last_scenario == scenario:
            result = database.update_end(session['user_id'])
            if result == True:
                success_message = "The game is over"
                flash(success_message, 'success')
                return redirect(url_for('game_of_life.end'))
            else:
                current_app.logger.error(result)
                error_message = "Something went wrong :((("
                flash(error_message, 'error')
                return redirect(url_for('game_of_life.scenarios', scenario=scenario))


        
        return redirect(url_for('game_of_life.scenarios',scenario=scenario+1))
        

    if g.user['progress'] == 0:
        error_message = 'Please click the play button to proceed'
        flash(error_message, 'error')
        return redirect(url_for('game_of_life.begin'))
    
    if g.user['progress'] != scenario:
        error_message = "Redirected back"
        flash(error_message, 'error')
        return redirect(url_for('game_of_life.scenarios', scenario=g.user['progress']))
    
    return render_template('game/scenario.html', scenario=scenario, character_info=g.user['character'])


@bp.route('/end', methods=['GET','POST'])
@login_required
def end():
    
    if request.method == 'POST':
        choice = request.form['choice']
        if choice is None:
            error_message = "Invalid input"
            flash(error_message, 'error')
            return redirect(url_for('game_of_life.end'))
        
        if choice == 'restart':
            result = database.delete_character(session['user_id'])
            if result == True:
                success_message = "Game restarted"
                flash(success_message, 'success')
                return redirect(url_for('game_of_life.begin'))
            else:
                current_app.logger.error(result)
                error_message = "Something went wrong"
                flash(error_message, 'error')
                return redirect(url_for("game_of_life.begin"))

    if g.user['end'] == False or g.user.get('end') is None:
        error_message = "Your game has not ended yet"
        flash(error_message, 'error')
        return redirect(url_for("game_of_life.begin"))

    return render_template('game/end.html')
    


@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        character_name = request.form['name']
        character_funds = float(request.form['funds'])

        if character_name is None:
            error_message = "Character name is required"
            flash(error_message, 'error')
            return redirect(url_for('game_of_life.create'))
        elif character_funds < 0:
            error_message = "Please input a positive number"
            flash(error_message, 'error')
            return redirect(url_for('game_of_life.create'))
        
        result = database.add_character(session['user_id'], character_name, character_funds)

        if result == True:
            success_message = "Character created!"
            flash(success_message, 'success')
            return redirect(url_for("game_of_life.begin"))
        else:
            error_message = "Something went wrong :(."
            flash(error_message,'error')
            return redirect(url_for('game_of_life.create'))

    return render_template('game/create.html')


# @bp.route('/update', methods=['GET', 'POST'])
# @login_required
# def update():
#     db = get_db()
#     character_id = ObjectId(session['character_id'])
#     query = {"_id": character_id}
#     find_character = db.character.find_one(query)
#     error_message = None

#     if find_character is None:
#         error_message = "No character found"
#         flash(error_message, 'error')
#         return redirect(url_for('game_of_life.begin'))
    

#     if request.method == 'POST':

#         new_name = request.form['name']
#         new_fund = float(request.form['funds'])

#         if new_name is None:
#             error_message = "Name cannot be empty"
        
#         if new_fund < 0:
#             error_message = "Please input a positive integer value"
        
#         if error_message is None:

#             # Update value for character_info
#             character_info = {
#                 "name" : new_name,
#                 "funds" : new_fund,
#                 "updated_at": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
#             }


#         query = {"_id": character_id}
#         value = {"$set": character_info}
#         db.character.update_one(query, value)
#         success_message = "Character updated!"
#         flash(success_message, 'success')
#         return redirect(url_for('game_of_life.begin'))

    

#     return render_template('game/update.html',character_info=find_character)