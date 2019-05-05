import functools, random

from flask import (
    Blueprint, flash, g, request, jsonify
)

from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token, get_jwt_identity
)

from assassin_server.__init__ import internal_error
from assassin_server import db_models
from assassin_server.db_models import table_to_dict
db = db_models.db

bp = Blueprint('creator_access', __name__, url_prefix='/creator_access')


@bp.route('/create_game', methods=['POST'])
def create_game():
    """Creates a game in the data base with the specified name and rules, and returns the game code for that game."""
    content = request.get_json()

    game_name=content['game_name']
    game_rules=content['game_rules']

    if game_name is None:
        return (internal_error(7), 400)

    is_unique=False
    attempts=0
    min_code=1000
    max_code=9999

    # guarentees that game_code is UNIQUE
    while not is_unique:
        game_code=random.randint(min_code, max_code+1)

        if db.session.query(
                db_models.Games.game_id
            ).filter_by(
                game_code=game_code
            ).scalar() is None: # pattern from https://stackoverflow.com/questions/32938475/flask-sqlalchemy-check-if-row-exists-in-table
            is_unique=True

        attempts=attempts+1
        if attempts>(max_code-min_code):
            return (internal_error(8), 500)

    new_game = db_models.Games(
        game_name = game_name,
        game_rules = game_rules,
        game_code = game_code,
        game_state = 0
        )
    db.session.add(new_game)
    db.session.commit()

    output = {
        'game_code': game_code
    }

    return jsonify(output)

# Doesn't check if targets already exists. Not sure if this is a problem
# Trying to reassign targets will make UNIQUE constraint on target id fail, return a 500
@bp.route('/start_hunt', methods=['GET'])
@jwt_required
def start_hunt():
    """Starts the hunting phase of the game"""
    #finds the id of whoever sent the token
    player_id = get_jwt_identity()

    is_creator = db.session.query(
            db_models.Players.is_creator
        ).filter_by(
            player_id = player_id
        ).first().is_creator


    # checks the accessor is the creator
    if is_creator == 0:
        return (internal_error(6), 403)

    # grabs the game code
    game_code = db.session.query(
            db_models.Players.game_code
        ).filter_by(
            player_id = player_id
        ).first().game_code

    #checks if the player is the only player
    if len(db.session.query(
            db_models.Players.player_id
        ).filter_by(
            game_code = game_code
        ).all())<2:
        return jsonify({'win' : True}), 200


    players_with_target=generate_targets(game_code)

    #give players targets
    for player in players_with_target:

        player_from_db = db.session.query(
                db_models.Players
            ).filter_by(
                player_id=player['player_id']
            ).first()

        player_from_db.target_first_name = player['target_first_name']
        player_from_db.target_last_name = player['target_last_name']
        player_from_db.target_id = player['target_id']

    db.session.commit()


    #update game_state
    game = db.session.query(
            db_models.Games
        ).filter_by(
            game_code = game_code
        ).first()
    db.session.commit()


    return jsonify({'win' : False}), 200

@bp.route('/player_list', methods=['GET'])
@jwt_required
def player_list():
    #finds the id of whoever sent the token
    player_id = get_jwt_identity()

    creator_info = db.session.query(
            db_models.Players.is_creator,
            db_models.Players.game_code
        ).filter_by(
            player_id = player_id
        ).first()

    if not creator_info.is_creator :
        return (internal_error(6), 403)

    player_list = db.session.query(
            db_models.Players.player_first_name,
            db_models.Players.player_last_name
        ).filter_by(
            game_code = creator_info.game_code
        ).all()

    return jsonify({"players": player_list})




#gives each player a target that fits the rules of the game
def generate_targets(game_code):

    players_with_target=[]
    players_without_target=db_models.table_to_dict(
        db.session.query(
                db_models.Players
            ).filter_by(
                game_code=game_code
            ).all()
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
