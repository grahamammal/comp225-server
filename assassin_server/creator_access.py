import functools, random

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify
)

from assassin_server.db import get_db, row_to_dict

bp = Blueprint('creator_access', __name__, url_prefix='/creator_access')

## TODO: finish this
@bp.route('/start_hunt', methods=['GET'])
def start_hunt():
    """Starts the hunting phase of the game"""

    player_id=session['this_player_id']

    db=get_db()

    creator_status= db.execute(
        'SELECT is_creator FROM players'
        ' WHERE player_id = ?',
        (player_id,)
    ).fetchone()

    if creator_status is None:
        return "Attempting to create game while not being a player"
    elif creator_status is 0:
        return "You are not the creator"

    
    return None


@bp.route('/create_game', methods=['POST'])
def create_game():
    """Creates a game in the data base with the specified name and rules, and returns the game code for that game."""
    content = request.get_json()

    game_name=content['game_name']
    game_rules=content['game_rules']

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
        ' (game_name, game_rules, game_code, game_state)'
        ' VALUES (?, ?, ?, 0)',
        (game_name, game_rules, game_code)
    )
    db.commit()

    game_code_json = {
        'game_code': game_code
    }

    return jsonify(game_code_json)
