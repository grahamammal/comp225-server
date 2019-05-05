import functools, random
from flask import (
    Blueprint, g, request, url_for, jsonify
)

from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token, get_jwt_identity
)

from assassin_server.__init__ import internal_error
from assassin_server.db_models import Players, Games, db, table_to_dict


bp = Blueprint('player_access', __name__, url_prefix='/player_access')

@bp.route('/add_player', methods=['POST'])
def add_player():
    """Adds a player with the given name to the game with the given game code"""

    content = request.get_json()

    player_first_name=content['player_first_name']
    player_last_name=content['player_last_name']
    is_creator=content['is_creator']
    game_code=content['game_code']



    #checks if the game exists
    if  db.session.query(
            Games.game_id
        ).filter_by(
            game_code=game_code
        ).scalar() is None:
        return (internal_error(0), 400)


    #checks if the game already started
    if  db.session.query(
            Games.game_state
        ).filter_by(
            game_code=game_code
        ).first().game_state == 1:
        return (internal_error(1), 400)


    #checks if player already exists
    if db.session.query(
            Players.player_id
        ).filter_by(
            player_first_name = player_first_name,
            player_last_name = player_last_name,
            game_code = game_code
        ).scalar() is not None:
        return (internal_error(2), 400)


    #checks if there is already a creator of the game
    if db.session.query(
            Players.player_id
        ).filter_by(
            game_code = game_code,
            is_creator = True
        ).scalar() is not None and str(is_creator) == str(1):
        return (internal_error(3), 400)

    #adds player to database if nothing went wrong

    min_kill_code = 1000
    max_kill_code = 9999

    player_kill_code= random.randint(min_kill_code, max_kill_code)


    player = Players(
        player_first_name = player_first_name,
        player_last_name = player_last_name,
        is_creator = str(is_creator) == str(1),
        is_alive = True,
        player_kill_code = player_kill_code,
        game_code = game_code
        )
    db.session.add(player)
    db.session.commit()


    player_id = db.session.query(
            Players.player_id
        ).filter_by(
            player_first_name=player_first_name,
            player_last_name=player_last_name,
            game_code=game_code
        ).first().player_id

    access_token=create_access_token(identity=player_id)


    output = {
        'player_kill_code': player_kill_code,
        'access_token' : access_token
    }


    return jsonify(output)

# May want to add a way to ensure this is sent from our app
@bp.route('/got_target', methods=['POST'])
@jwt_required
def got_target():
    #finds the id of whoever sent the token
    player_id = get_jwt_identity()
    #asking the player to provide their target's kill code
    content=request.get_json()
    guessed_target_kill_code = content['guessed_target_kill_code']

    #checks that the player is alive
    is_alive = db.session.query(
            Players.is_alive
        ).filter_by(
            player_id = player_id
        ).first().is_alive

    if not is_alive:
        return (internal_error(9), 400)


    target_id = db.session.query(
            Players.target_id
        ).filter_by(
            player_id = player_id
        ).first().target_id

    #checks that the player has a target
    if target_id is None:
        return (internal_error(5), 400)

    #this is the actual target's kill code
    target_kill_code = db.session.query(
            Players.player_kill_code
        ).filter_by(
            player_id = target_id
        ).first().player_kill_code

    if str(guessed_target_kill_code) != str(target_kill_code):
        return(internal_error(10), 400)

    # retrieve the target of your target
    new_target_info = db.session.query(
            Players.target_first_name,
            Players.target_last_name,
            Players.target_id
        ).filter_by(
            player_id = target_id
        ).first()

    # set your target to dead
    target = db.session.query(
            Players
        ).filter_by(
            player_id=target_id
        ).first()

    target.is_alive = False

    #set the target of your target to your target
    player = db.session.query(
            Players
        ).filter_by(
            player_id = player_id
        ).first()
    player.target_first_name = new_target_info.target_first_name
    player.target_last_name = new_target_info.target_last_name
    player.target_id = new_target_info.target_id

    db.session.commit()
    #checks if you just got the second to last player, meaning you won
    if player_id is new_target_info.target_id:
        return jsonify({"win": True}), 200

    return jsonify({"win": False}), 200


@bp.route('/get_game_info',  methods=['POST'])
def get_game_info():
    content=request.get_json()
    game_code=content["game_code"]

    info = db.session.query(
            Games.game_rules,
            Games.game_name
        ).filter_by(
            game_code = game_code
        ).first()

    if info is None:
        return (internal_error(0), 400)

    return jsonify({'game_rules': info.game_rules, 'game_name' : info.game_name})

#may want to ensure request is sent from app
@bp.route('/request_target', methods=['GET'])
@jwt_required
def request_target():
    """Requests the target of the player who made the request, using that players session info"""

    #finds the id of whoever sent the token
    player_id = get_jwt_identity()

    target = db.session.query(
            Players.target_first_name,
            Players.target_last_name
        ).filter_by(
            player_id = player_id
        ).first()

    if target.target_first_name is None and target.target_last_name is None:
        return (internal_error(5), 400)


    return jsonify({'target_first_name' : target.target_first_name, 'target_last_name' : target.target_last_name})


@bp.route('/remove_from_game', methods=['GET'])
@jwt_required
def remove_from_game():

    #finds the id of whoever sent the token
    player_id = get_jwt_identity()

    #check if the player won the game already
    game_code = db.session.query(
            Players.game_code
        ).filter_by(
            player_id = player_id
        ).first()

    if game_code is None:
        return (internal_error(4), 403)

    all_players = db.session.query(
            Players.player_id
        ).filter_by(
            game_code = game_code.game_code,
            is_alive = True,
        ).all()

    if len(all_players) == 1:
        player = db.session.query(
                Players
            ).filter_by(
                player_id = player_id
            ).delete()

        db.session.query(
                Games
            ).filter_by(
                game_code = game_code.game_code
            ).delete()
        db.session.commit()

        return jsonify({'message' : 'success'}), 200


    is_alive = db.session.query(
            Players.is_alive
        ).filter_by(
            player_id = player_id
        ).first().is_alive

    #check if player is Alive
    if is_alive:
        return (internal_error(9), 400)

    #remove them from the game
    db.session.query(
            Players
        ).filter_by(
            player_id = player_id
        ).delete()

    db.session.commit()

    return jsonify({'message' : 'success'}), 200


@bp.route('/quit_game', methods = ['GET'])
@jwt_required
def quit_game():
    #finds the id of whoever sent the token
    player_id = get_jwt_identity()

    # get the players game
    game_code = db.session.query(
            Players.game_code
        ).filter_by(
            player_id = player_id
        ).first().game_code

    # get the players target
    target_info = db.session.query(
            Players.target_first_name,
            Players.target_last_name,
            Players.target_id
        ).filter_by(
            player_id = player_id
        ).first()

    # remove the player from the game
    db.session.query(
            Players
        ).filter_by(
            player_id = player_id
        ).delete()


    #check if the game is started
    if target_info[0] is not None:
        # set the target of the quitter to be the quitters target
        player = db.session.query(
                Players
            ).filter_by(
                target_id = player_id
            ).first()
        player.target_first_name = target_info.target_first_name
        player.target_last_name = target_info.target_last_name
        player.target_id = target_info.target_id

        # if theres only one player left set the game to won
        all_players = db.session.query(
                Players.player_id
            ).filter_by(
                game_code = game_code
            ).all()

        if len(all_players) == 1:
            game = db.session.query(
                    Games
                ).filter_by(
                    game_code = game_code
                ).first()
            game.game_state = 2


    db.session.commit()
    return jsonify({'message' : 'success'}), 200
