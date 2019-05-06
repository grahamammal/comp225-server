import functools, random

from flask import (
    Blueprint, flash, g, redirect, request, url_for, jsonify
)
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)

from assassin_server.__init__ import internal_error
from assassin_server.db_models import Players, Games, db, table_to_dict

bp = Blueprint('status_access', __name__, url_prefix='/status_access')

@bp.route('/is_alive', methods = ['GET'])
@jwt_required
def is_alive():
    # finds the id of whoever sent the token
    player_id = get_jwt_identity()

    is_alive = db.session.query(
            Players.is_alive
        ).filter_by(
            player_id = player_id
        ).first()

    # make sure the player is alive
    if is_alive is None:
        return (internal_error(4), 403)

    return jsonify({'is_alive':is_alive.is_alive})


@bp.route('/game_state', methods=['POST'])
def is_game_started():
    content=request.get_json()
    game_code=content["game_code"]

    game_state = db.session.query(
            Games.game_state
        ).filter_by(
            game_code = game_code
        ).first()

    # makes sure the game exists
    if game_state is None:
        return(internal_error(5), 400)

    return jsonify({'game_state':game_state.game_state})
