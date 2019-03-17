import functools, random

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify, abort, redirect, url_for
)

from assassin_server.db import get_db, row_to_dict

bp = Blueprint('player_access', __name__, url_prefix='/player_access')

@bp.route('/add_player',  methods=['POST'])
def add_player():
    """Adds a player with the given name to the game with the given game code"""

    content = request.get_json()

    player_first_name=content['player_first_name']
    player_last_name=content['player_last_name']
    is_creator=content['is_creator']
    game_code=content['game_code']

    error=None

    db=get_db()

    #checks if the game exists
    if db.execute(
        'SELECT game_id FROM games'
        ' WHERE game_code = ?',
        (game_code,)
    ).fetchone() is None:
        error=400

    #checks if player already exists
    if db.execute(
        'SELECT player_id FROM players'
        ' WHERE player_first_name = ? AND player_last_name=? AND game_code = ?',
        (player_first_name, player_last_name, game_code)
    ).fetchone() is not None:
        error= 400

    #checks if there is already a creator of the game
    if db.execute(
        'SELECT player_id FROM players'
        ' WHERE game_code = ? AND is_creator = 1',
        (game_code,)
    ).fetchone() is not None and is_creator is 1:
        error= 400

    #adds player to database if nothing went wrong
    if error is None:
        db.execute(
            'INSERT INTO players'
            ' (player_first_name, player_last_name,is_creator, game_code, is_alive, disputed_Got)'
            ' VALUES (?, ?, ?, ?, 1, 0)',
            (player_first_name, player_last_name, is_creator, game_code)
        )
        db.commit()

        session['this_player_id']=db.execute(
            'SELECT player_id FROM players'
            ' WHERE player_first_name = ? AND player_last_name=? AND game_code = ?',
            (player_first_name, player_last_name, game_code)
        ).fetchone()[0]

    if error is not None:
        abort(error)

    return ('', 200)

# May want to add a way to ensure this is sent from our app
@bp.route('/got_target')
def got_target():

    player_id=session["this_player_id"]
    db=get_db()

    target_id=db.execute(
        'SELECT target_id FROM players'
        ' WHERE player_id = ?',
        (player_id, )
    ).fetchone()[0]

    #checks that the player has a target
    if target_id is None:
        abort(400)

    #retrieve the target of your target
    new_target=row_to_dict(
        db.execute(
            'SELECT target_first_name, target_last_name, target_id FROM players'
            ' WHERE player_id = ?',
            (target_id, )
        ).fetchone()
    )

    #checks if you just got the second to last player, meaning you won
    if player_id is new_target["target_id"]:
        return redirect(url_for('won_game'))

    #remove your target
    db.execute(
        'DELETE FROM players'
        ' WHERE player_id = ?',
        (target_id,)
    )

    #set the target of your target to your target
    db.execute(
        'UPDATE players'
        ' SET target_first_name = ?, target_last_name = ?, target_id = ?'
        ' WHERE player_id = ?',
        (new_target['target_first_name'], new_target['target_last_name'], new_target['target_id'],
         player_id)
    )
    db.commit()



    return ('', 200)


@bp.route('/won_game')
def won_game():
    return jsonify({"win": True})

@bp.route('/get_game_rules',  methods=['POST'])
def get_game_rules():
    content=request.get_json()

    game_code=content["game_code"]


    db=get_db()
    rules=db.execute(
        'SELECT game_rules FROM games'
        ' WHERE game_code = ?',
        (game_code,)
    ).fetchone()

    output=row_to_dict(rules)
    return jsonify(output)

#may want to ensure request is sent from app
@bp.route('/request_target', methods=['GET'])
def request_target():
    """Requests the target of the player who made the request, using that players session info"""

    player_id=session['this_player_id']



    db=get_db()
    target= db.execute(
        'SELECT target_first_name, target_last_name, target_id FROM players'
        ' WHERE player_id = ?',
        (player_id,)
    ).fetchone()



    if target is None:
        abort(400) #the player has no target

    output=row_to_dict(target)
    return jsonify(output)
