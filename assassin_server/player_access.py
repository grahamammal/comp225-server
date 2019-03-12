import functools, random

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify
)
from werkzeug.security import check_password_hash, generate_password_hash

from assassin_server.db import get_db

bp = Blueprint('player_access', __name__, url_prefix='/player_access')

@bp.route('/add_player',  methods=['POST'])
def add_player():
    """Adds a player with the given name to the game with the given game code, returns whether the name already exists or not"""
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
@bp.route('/request_target', methods=['GET'])
def request_target():
    """Requests the target of the player who made the request, using that players session info"""

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


@bp.route('/create_game', methods=['POST'])
def create_game():
    """Creates a game in the data base with the specified name, and returns the game code for that game."""
    content = request.get_json()

    game_name=content['game_name']

    db=get_db()

    is_unique=False
    attempts=0
    min_code=1000
    max_code=9999

    #guarentees that game_code is UNIQUE
    while not is_unique:
        game_code=random.randint(min_code, max_code+1)

        if db.execute(
            'SELECT game_code FROM games'
            ' WHERE game_code = ?',
            (game_code,)
        ).fetchone() is None:
            is_unique=True

        attempts=attempts+1
        if attempts>(max_code-min_code):
            return "No more game codes"



    db.execute(
        'INSERT INTO games'
        ' (game_name, game_code, game_state)'
        ' VALUES (?, ?, 0)',
        (game_name, game_code)
    )
    db.commit()

    game_code_json = {
        'game_code': game_code
    }

    return jsonify(game_code_json)
