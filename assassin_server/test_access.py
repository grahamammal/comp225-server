#THIS SHOULD BE DELETED BEFORE WE RELEASE IT
import functools, random

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify
)

from assassin_server.db import get_db, row_to_dict, table_to_dict

bp = Blueprint('test_access', __name__, url_prefix='/test_access')

@bp.route('/get_player', methods=['POST'])
def get_player():
    """Returns all the information of a specified player for testing"""

    content = request.get_json()
    db=get_db()

    player_first_name=content['player_first_name']
    player_last_name=content['player_last_name']
    game_code=content['game_code']

    if db.execute(
        'SELECT * FROM players'
        ' WHERE player_first_name = ? AND player_last_name=? AND game_code = ?',
        (player_first_name, player_last_name, game_code)
    ).fetchone() is None:
        return "There is no such player"

    player=db.execute(
        'SELECT * FROM players'
        ' WHERE player_first_name = ? AND player_last_name=? AND game_code = ?',
        (player_first_name, player_last_name, game_code)
    ).fetchone()


    player_json=row_to_dict(player)

    return jsonify(player_json)


@bp.route('/get_game', methods=['POST'])
def get_game():
    """Returns a single game"""

    content = request.get_json()
    db=get_db()

    game_code=content["game_code"]

    if db.execute(
        'SELECT * FROM games'
        ' WHERE game_code = ?',
        (game_code,)
    ).fetchone() is None:
        return "There is no such game"

    game=db.execute(
        'SELECT * FROM games'
        ' WHERE game_code = ?',
        (game_code,)
    ).fetchone()


    game_json=row_to_dict(game)

    return jsonify(game_json)


@bp.route('/get_all_players', methods=['GET'])
def get_all_players():
    """Returns every player in the table for testing"""

    db=get_db()

    players=db.execute(
        'SELECT * FROM players'
    ).fetchall()

    return jsonify(table_to_dict(players))


@bp.route('/get_all_games', methods=['GET'])
def get_all_games():
    """Returns all the info on all the games"""


    db=get_db()

    games=db.execute(
        'SELECT * FROM games'
    ).fetchall()


    return jsonify(table_to_dict(games))
