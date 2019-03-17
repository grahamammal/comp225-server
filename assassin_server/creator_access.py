import functools, random

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify, abort
)

from assassin_server.db import get_db, row_to_dict, table_to_dict

bp = Blueprint('creator_access', __name__, url_prefix='/creator_access')

# Doesn't check if targets already exists. Not sure if this is a problem
# Trying to reassign targets will make UNIQUE constraint on target id fail, return a 500
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
            abort(500)#there are no game codes left



    db.execute(
        'INSERT INTO games'
        ' (game_name, game_rules, game_code, game_state)'
        ' VALUES (?, ?, ?, 0)',
        (game_name, game_rules, game_code)
    )
    db.commit()

    output = {
        'game_code': game_code
    }

    return jsonify(output)

#gives each player a target that fits the rules of the game
def generate_targets(game_code):
    db=get_db()

    players_with_target=[]
    players_without_target=table_to_dict(
        db.execute(
            'SELECT player_id, player_first_name, player_last_name FROM players'
            ' WHERE game_code = ?',
            (game_code,)
        ).fetchall()
    )

    #give a target to the n-1 players
    n=len(players_without_target)
    last_assigned_target_index=0
    for i in range(0, n-1):
        players_with_target.append(
            players_without_target.pop(last_assigned_target_index)
        )

        last_assigned_target_index=random.randint(0, len(players_without_target)-1)


        players_with_target[i]["target_first_name"]=players_without_target[last_assigned_target_index]["player_first_name"]
        players_with_target[i]["target_last_name"]=players_without_target[last_assigned_target_index]["player_last_name"]
        players_with_target[i]["target_id"]=players_without_target[last_assigned_target_index]["player_id"]

    #give a target to the last player
    players_with_target.append(
        players_without_target.pop(0)
    )

    players_with_target[n-1]["target_first_name"]=players_with_target[0]["player_first_name"]
    players_with_target[n-1]["target_last_name"]=players_with_target[0]["player_last_name"]
    players_with_target[n-1]["target_id"]=players_with_target[0]["player_id"]


    return players_with_target
