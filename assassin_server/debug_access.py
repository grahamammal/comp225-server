#THIS SHOULD BE DELETED BEFORE WE RELEASE IT
import functools, random

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify
)

from assassin_server.creator_access import generate_targets
from assassin_server.db_models import Players, Games, db, table_to_dict

bp = Blueprint('test_access', __name__, url_prefix='/test_access')

@bp.route('/get_all_players', methods=['GET'])
def get_all_players():
    players = db.session.query(
            Players
        ).all()

    return jsonify(table_to_dict(players))


@bp.route('/get_all_games', methods=['GET'])
def get_all_games():
    games = db.session.query(
            Games
        ).all()

    return jsonify(table_to_dict(games))
