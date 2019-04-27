import functools, random

from flask import (
    Blueprint, flash, g, redirect, request, url_for, jsonify
)

from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)

from assassin_server.db import get_db, row_to_dict
from assassin_server.__init__ import internal_error

bp = Blueprint('status_access', __name__, url_prefix='/status_access')

@bp.route('/is_alive', methods = ['GET'])
@jwt_required
def is_alive():
    #finds the id of whoever sent the token
    player_id = get_jwt_identity()

    db=get_db()
    is_alive=db.execute(
        'SELECT is_alive FROM players'
        ' WHERE player_id=?',
        (player_id,)
    ).fetchone()

    if is_alive is None:
        return (internal_error(4), 403)

    return jsonify(row_to_dict(is_alive))

@bp.route('/game_state', methods=['POST'])
def is_game_started():
    content=request.get_json()
    game_code=content["game_code"]

    db=get_db()
    game_state=db.execute(
        'SELECT game_state FROM games'
        ' WHERE game_code=?',
        (game_code,)
    ).fetchone()

    if game_state is None:
        return(internal_error(5), 400)

    return jsonify(row_to_dict(game_state))
