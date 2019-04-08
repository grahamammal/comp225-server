import functools, random

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify, abort, redirect, url_for
)

from assassin_server.db import get_db, row_to_dict
from assassin_server.__init__ import internal_error

bp = Blueprint('status_access', __name__, url_prefix='/status_access')

@bp.route('/is_alive')
def is_alive():

    if 'this_player_id' not in session:
        return (internal_error(4), 403)

    player_id=session['this_player_id']

    db=get_db()
    is_alive=db.execute(
        'SELECT is_alive FROM players'
        ' WHERE player_id=?',
        (player_id,)
    ).fetchone()

    if is_alive is None:
        return (internal_error(4), 403)

    return jsonify(row_to_dict(is_alive))

@bp.route('/is_game_started', methods=['POST'])
def is_game_started():

    content=request.get_json()
    game_code=content["game_code"]

    player_id=session['this_player_id']

    db=get_db()
    game_code=db.execute(
        'SELECT game_code FROM players'
        ' WHERE player_id=?',
        (player_id,)
    ).fetchone()[0]



    is_game_started=db.execute(
        'SELECT game_state FROM games'
        ' WHERE game_code=?',
        (game_code,)
    ).fetchone()


    if is_game_started is None:
        return('Something went very wrong', 500)

    return jsonify(row_to_dict(is_game_started))
