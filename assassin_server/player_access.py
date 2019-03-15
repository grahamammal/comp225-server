import functools, random

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify
)

from assassin_server.db import get_db, row_to_dict

bp = Blueprint('player_access', __name__, url_prefix='/player_access')

@bp.route('/add_player',  methods=['POST'])
def add_player():
    """Adds a player with the given name to the game with the given game code, returns whether the name already exists or not"""

    content = request.get_json()

    player_first_name=content['player_first_name']
    player_last_name=content['player_last_name']
    is_creator=content['is_creator']

    game_code=content['game_code']

    error=None

    db=get_db()
    #checks if player already exists
    if db.execute(
        'SELECT player_id FROM players'
        ' WHERE player_first_name = ? AND player_last_name=? AND game_code = ?',
        (player_first_name, player_last_name, game_code)
    ).fetchone() is not None:
        error= 'Player already exists'

    if db.execute(
        'SELECT player_id FROM players'
        ' WHERE game_code = ? AND is_creator = 1',
        (game_code,)
    ).fetchone() is not None and is_creator is 1:
        error= 'Creator already exists'

    #adds player to database
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

    return str(error)

# TODO: finish this
@bp.route('/got_player')
def got_player():

    return None


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



    if target is not None:
        target_json = row_to_dict(target)
    else:
        return "This player has no target"
    return jsonify(target_json)
