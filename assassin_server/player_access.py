import functools, random

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify, abort, redirect, url_for
)

from assassin_server.db import get_db, row_to_dict
from assassin_server.__init__ import internal_error

bp = Blueprint('player_access', __name__, url_prefix='/player_access')

@bp.route('/add_player',  methods=['POST'])
def add_player():
    """Adds a player with the given name to the game with the given game code"""

    content = request.get_json()

    player_first_name=content['player_first_name']
    player_last_name=content['player_last_name']
    is_creator=content['is_creator']
    game_code=content['game_code']

    db=get_db()

    #checks if the game exists
    if db.execute(
        'SELECT game_id FROM games'
        ' WHERE game_code = ?',
        (game_code,)
    ).fetchone() is None:
        return (internal_error(0), 400)

    #checks if the game already started
    if db.execute(
        'SELECT game_state FROM games'
        ' WHERE game_code = ?',
        (game_code,)
    ).fetchone()[0] is 1:
        return (internal_error(1), 400)

    #checks if player already exists
    if db.execute(
        'SELECT player_id FROM players'
        ' WHERE player_first_name = ? AND player_last_name=? AND game_code = ?',
        (player_first_name, player_last_name, game_code)
    ).fetchone() is not None:
        return (internal_error(2), 400)




    #checks if there is already a creator of the game
    if db.execute(
        'SELECT player_id FROM players'
        ' WHERE game_code = ? AND is_creator = 1',
        (game_code,)
    ).fetchone() is not None and str(is_creator) == str(1):
        return (internal_error(3), 400)

    #adds player to database if nothing went wrong

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


    return ('', 200)

# May want to add a way to ensure this is sent from our app
@bp.route('/got_target')
def got_target():
    #makes sure your session has a player associated with it
    if 'this_player_id' not in session:
        return (internal_error(4), 403)

    player_id=session.get("this_player_id", None)


    db=get_db()

    #checks that the player is alive
    is_alive=db.execute(
        'SELECT is_alive FROM players'
        ' WHERE player_id = ?',
        (player_id, )
    ).fetchone()[0]

    if str(is_alive)==str(0):
        return (internal_error(9), 400)

    #checks that the player has a target
    if target_id[0] is None:
        return (internal_error(5), 400)

    target_id=db.execute(
        'SELECT target_id FROM players'
        ' WHERE player_id = ?',
        (player_id, )
    ).fetchone()

    #checks that the player has a target
    if target_id[0] is None:
        return (internal_error(5), 400)

    else:
        target_id=target_id[0]
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
        return redirect(url_for('player_access.won_game'))

    #kill your target
    db.execute(
        'UPDATE players'
        ' SET is_alive = 0'
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

@bp.route('/get_game_info',  methods=['POST'])
def get_game_info():
    content=request.get_json()
    game_code=content["game_code"]

    db=get_db()
    info=db.execute(
        'SELECT game_rules, game_name FROM games'
        ' WHERE game_code = ?',
        (game_code,)
    ).fetchone()

    if info is None:
        return (internal_error(0), 400)

    output=row_to_dict(info)
    return jsonify(output)

#may want to ensure request is sent from app
@bp.route('/request_target', methods=['GET'])
def request_target():
    """Requests the target of the player who made the request, using that players session info"""
    #makes sure your session has a player associated with it
    if 'this_player_id' not in session:
        return (internal_error(4), 403)


    player_id=session['this_player_id']



    db=get_db()
    target= db.execute(
        'SELECT target_first_name, target_last_name, target_id FROM players'
        ' WHERE player_id = ?',
        (player_id,)
    ).fetchone()



    if target[0] is None and target[1] is None and target[2] is None:
        return (internal_error(5), 400)

    output=row_to_dict(target)
    return jsonify(output)

@bp.route('/remove_from_game', methods=['GET'])
def remove_from_game():
    if 'this_player_id' not in session:
        return (internal_error(4), 403)

    player_id=session['this_player_id']
