#THIS SHOULD BE DELETED BEFORE WE RELEASE IT
import functools, random

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify
)

from assassin_server.db import get_db, row_to_dict, table_to_dict
from assassin_server.creator_access import generate_targets

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

@bp.route('/got_target', methods=['POST'])
def got_target():
    """The exact same method as got_target in player access, but you can specify a player to act as"""
    content=request.get_json()
    db=get_db()

    player_id=content['player_id']

    target_id=db.execute(
        'SELECT target_id FROM players'
        ' WHERE player_id = ?',
        (player_id, )
    ).fetchone()[0]

    #checks that the player has a target
    if target_id is None:
        abort(400)

    #retrieve the target of your target
    new_target=row_to_dict(
        db.execute(
            'SELECT target_first_name, target_last_name, target_id FROM players'
            ' WHERE player_id = ?',
            (target_id, )
        ).fetchone()
    )

    #checks if you just got the second to last player, meaning you won
    if player_id is new_target['target_id']:
        return jsonify({'won':True})

    #remove your target
    db.execute(
        'DELETE FROM players'
        ' WHERE player_id = ?',
        (target_id,)
    )

    #set the target of your target to your target
    db.execute(
        'UPDATE players'
        ' SET target_first_name = ?, target_last_name = ?, target_id = ?'
        ' WHERE player_id = ?',
        (new_target['target_first_name'], new_target['target_last_name'], new_target['target_id'],
         player_id)
    )
    db.commit()



    return ('', 200)


@bp.route('/start_hunt', methods=['POST'])
def start_hunt():
    """Exact same as start hunt from creator access, except we can act as any player when starting the game"""
    content=request.json()

    player_id=content['player_id']

    db=get_db()

    creator_status= db.execute(
        'SELECT is_creator FROM players'
        ' WHERE player_id = ?',
        (player_id,)
    ).fetchone()

    #forbidden if the player isn't the creator or if the player doesn't exist
    if creator_status is None or creator_status[0] is 0:
        abort(403)

    game_id=db.execute(
        'SELECT game_code FROM players'
        ' WHERE player_id = ?',
        (player_id,)
    ).fetchone()[0]

    players_with_target=generate_targets(game_id)

    for player in players_with_target:
        #not sure why I need to do this but it didn't work when I placed the dictionary access in the sql query
        target_first_name=player["target_first_name"]
        target_last_name=player["target_last_name"]
        target_id=player["target_id"]
        player_first_name=player["player_first_name"]
        player_last_name=player["player_last_name"]
        player_id=player["player_id"]
        db.execute(
            'UPDATE players'
            ' SET target_first_name = ?, target_last_name = ?, target_id = ?'
            ' WHERE player_id =?',
            (target_first_name, target_last_name, target_id,
            player_id)
        )
        db.commit()

    return ('', 200)
