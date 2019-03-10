import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify
)
from werkzeug.security import check_password_hash, generate_password_hash

from assassin_server.db import get_db

bp = Blueprint('player_access', __name__, url_prefix='/player_access')

@bp.route('/add_player')
def add_player():
    #doesn't check to make sure variables are valid
    player_name =request.args.get('player_name', None)
    game_code  = request.args.get('game_code', None)

    error=None


    db=get_db()
    if db.execute(
        'SELECT player_id FROM players'
        ' WHERE player_name = ? AND game_code = ?',
        (player_name, game_code)
    ).fetchone() is not None:
        error= "Player already exists"

    if error is None:
        db.execute(
            'INSERT INTO players (player_name, game_code, target_name) VALUES (?, ?, ?)',
            (player_name, game_code, target_name)
        )
        db.commit()

    return "Error: "+str(error)

#players can request data by providing their name and their game code
@bp.route('/request_target')
def request_target():
    #doesn't check to make sure variables are valid
    player_name  = request.args.get('player_name', None)
    game_code  = request.args.get('game_code', None)

    db=get_db()
    target_name=db.execute(
        'SELECT target_name FROM players'
        ' WHERE player_name= ? AND game_code = ?',
        (player_name, game_code)
    ).fetchone()

    if target_name is not None:
        target_map = {
            "target_name": target_name[0]
        }
    else:
        target_map={
            "target_name" : None
        }
    return jsonify(target_map)
