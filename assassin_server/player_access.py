import functools, random

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify
)
from werkzeug.security import check_password_hash, generate_password_hash

from assassin_server.db import get_db

bp = Blueprint('player_access', __name__, url_prefix='/player_access')

@bp.route('/add_player',  methods=['POST'])
def add_player():
    content = request.get_json()

    player_first_name=content['player_first_name']
    player_last_name=content['player_last_name']
    game_code=content['game_code']

    error=None

    db=get_db()
    if db.execute(
        'SELECT player_id FROM players'
        ' WHERE player_first_name = ? AND player_last_name=? AND game_code = ?',
        (player_first_name, player_last_name, game_code)
    ).fetchone() is not None:
        error= 'Player already exists'

    if error is None:
        db.execute(
            'INSERT INTO players'
            ' (player_first_name, player_last_name, game_code, is_alive, disputed_Got)'
            ' VALUES (?, ?, ?, 1, 0)',
            (player_first_name, player_last_name, game_code)
        )
        db.commit()

        session['this_player_id']=db.execute(
            'SELECT player_id FROM players'
            ' WHERE player_first_name = ? AND player_last_name=? AND game_code = ?',
            (player_first_name, player_last_name, game_code)
        ).fetchone()[0]

    temp= db.execute(
        'SELECT player_first_name FROM players'
        ' WHERE game_code = ?',
        (game_code,)
    ).fetchone()

    return str(error)

#players can request data by providing their name and their game code
@bp.route('/request_target')
def request_target():

    player_id=session['this_player_id']



    db=get_db()
    target_name=temp= db.execute(
        'SELECT target_first_name, target_last_name FROM players'
        ' WHERE player_id = ?',
        (player_id,)
    ).fetchone()



    if target_name is not None:
        target_map = {
            'target_first_name': target_name[0],
            'target_last_name': target_name[1]
        }
    else:
        target_map={
            'target_first_name' : None,
            'target_last_name' : None

        }
    return jsonify(target_map)

# TODO: go to add player thing next?? or maybe return nothing and thats handle through the game
@bp.route('/create_game', methods=['POST'])
def create_game():

    content = request.get_json()

    game_name=content['game_name']

    game_code=random.randint(1000,10000)

    db=get_db()
    db.execute(
        'INSERT INTO games'
        ' (game_name, game_code, game_state)'
        ' (?, ?, 0)',
        (game_name, game_code)
    )
    db.commit()

    return None
