#THIS SHOULD BE DELETED BEFORE WE RELEASE IT
import functools, random

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify
)

from assassin_server.db import get_db

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


    player_json={
        "player_id": player[0],
        "player_first_name": player[1],
        "player_last_name": player[2],
        "target_first_name": player[3],
        "target_last_name": player[4],
        "is_alive": player[5],
        "is_creator": player[6],
        "disputed_got": player[7],
        "game_code": player[8]
    }

    return jsonify(player_json)

@bp.route('/get_all_players', methods=['GET'])
def get_all_players():
    """Returns every player in the table for testing"""

    db=get_db()

    players=db.execute(
        'SELECT * FROM players'
    ).fetchall()
