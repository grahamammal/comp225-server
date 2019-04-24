import functools, random
from flask import (
    Blueprint, g, request, url_for, jsonify
)

from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token, get_jwt_identity
)

from assassin_server.db import get_db, row_to_dict
from assassin_server.__init__ import internal_error

bp = Blueprint('player_access', __name__, url_prefix='/player_access')

@bp.route('/add_player', methods=['POST'])
def add_player():
    """Adds a player with the given name to the game with the given game code"""

    content = request.get_json()

    player_first_name=content['player_first_name']
    player_last_name=content['player_last_name']
    is_creator=content['is_creator']
    game_code=content['game_code']


    db=get_db()

    #checks if the game exists
    if db.execute(
        'SELECT game_id FROM games'
        ' WHERE game_code = ?',
        (game_code,)
    ).fetchone() is None:
        return (internal_error(0), 400)

    #checks if the game already started
    if db.execute(
        'SELECT game_state FROM games'
        ' WHERE game_code = ?',
        (game_code,)
    ).fetchone()[0] is 1:
        return (internal_error(1), 400)

    #checks if player already exists
    if db.execute(
        'SELECT player_id FROM players'
        ' WHERE player_first_name = ? AND player_last_name=? AND game_code = ?',
        (player_first_name, player_last_name, game_code)
    ).fetchone() is not None:
        return (internal_error(2), 400)


    #checks if there is already a creator of the game
    if db.execute(
        'SELECT player_id FROM players'
        ' WHERE game_code = ? AND is_creator = 1',
        (game_code,)
    ).fetchone() is not None and str(is_creator) == str(1):
        return (internal_error(3), 400)

    #adds player to database if nothing went wrong

    used = False
    min_kill_code = 1000
    max_kill_code = 9999

    player_kill_code= random.randint(min_kill_code, max_kill_code)

    db.execute(
        'INSERT INTO players'
        ' (player_first_name, player_last_name,is_creator, game_code, is_alive, disputed_Got, player_kill_code)'
        ' VALUES (?, ?, ?, ?, 1, 0, ?)',
        (player_first_name, player_last_name, is_creator, game_code, player_kill_code)
    )
    db.commit()


    player_id=db.execute(
        'SELECT player_id FROM players'
        ' WHERE player_first_name = ? AND player_last_name=? AND game_code = ?',
        (player_first_name, player_last_name, game_code)
    ).fetchone()[0]

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


    db=get_db()

    #checks that the player is alive
    is_alive=db.execute(
        'SELECT is_alive FROM players'
        ' WHERE player_id = ?',
        (player_id, )
    ).fetchone()[0]

    if str(is_alive)==str(0):
        return (internal_error(9), 400)


    target_id=db.execute(
        'SELECT target_id FROM players'
        ' WHERE player_id = ?',
        (player_id, )
    ).fetchone()

    #checks that the player has a target
    if target_id[0] is None:
        return (internal_error(5), 400)

    else:
        target_id=target_id[0]

    #this is the actual target's kill code
    target_kill_code=db.execute(
        'SELECT player_kill_code FROM players'
        ' WHERE player_id = ?',
        (target_id, )
    ).fetchone()[0]

    if guessed_target_kill_code != target_kill_code:
        return(internal_error(10), 400)

    # retrieve the target of your target
    new_target=row_to_dict(
    db.execute(
            'SELECT target_first_name, target_last_name, target_id FROM players'
            ' WHERE player_id = ?',
            (target_id, )
        ).fetchone()
    )
    #kill your target
    db.execute(
        'UPDATE players'
        ' SET is_alive = 0'
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
    #checks if you just got the second to last player, meaning you won
    if player_id is new_target["target_id"]:
        return jsonify({"win": True}), 200

    return jsonify({"win": False}), 200


@bp.route('/get_game_info',  methods=['POST'])
def get_game_info():
    content=request.get_json()
    game_code=content["game_code"]

    db=get_db()
    info=db.execute(
        'SELECT game_rules, game_name FROM games'
        ' WHERE game_code = ?',
        (game_code,)
    ).fetchone()

    if info is None:
        return (internal_error(0), 400)

    output=row_to_dict(info)
    return jsonify(output)

#may want to ensure request is sent from app
@bp.route('/request_target', methods=['GET'])
@jwt_required
def request_target():
    """Requests the target of the player who made the request, using that players session info"""

    #finds the id of whoever sent the token
    player_id = get_jwt_identity()



    db=get_db()
    target= db.execute(
        'SELECT target_first_name, target_last_name FROM players'
        ' WHERE player_id = ?',
        (player_id,)
    ).fetchone()



    if target[0] is None and target[1] is None:
        return (internal_error(5), 400)

    output=row_to_dict(target)
    return jsonify(output)

#Returns the player's kill code
@bp.route('/request_kill_code', methods=['GET'])
@jwt_required
def request_kill_code():
    #finds the id of whoever sent the token
    player_id = get_jwt_identity()

    db = get_db()

    player_kill_code= db.execute(
        'SELECT player_kill_code FROM players'
        ' WHERE player_id = ?',
        (player_id,)
    ).fetchone()

    if player_kill_code is None:
        return (internal_error(4), 403)

    if player_kill_code[0] is None:
        return (internal_error(11), 400)

    output=row_to_dict(player_kill_code)
    return jsonify(output)

@bp.route('/remove_from_game', methods=['GET'])
@jwt_required
def remove_from_game():

    #finds the id of whoever sent the token
    player_id = get_jwt_identity()

    db=get_db()

    #check if the player won the game already
    game_code=db.execute(
        'SELECT game_code FROM players'
        ' WHERE player_id = ?',
        (player_id, )
    ).fetchone()

    if game_code is None:
        return (internal_error(4), 403)

    all_players=db.execute(
        'SELECT * FROM players'
        ' WHERE game_code = ? AND player_id != ? AND is_alive == 1',
        (game_code[0], player_id)
    ).fetchone()

    if all_players is None:
        db.execute(
            'DELETE FROM players'
            ' WHERE player_id = ?',
            (player_id, )
        )
        db.commit()

        db.execute(
            'DELETE FROM games'
            ' WHERE game_code = ?',
            (game_code[0], )
        )
        db.commit()

        return jsonify({'message' : 'success'}), 200


    is_alive = db.execute(
        'SELECT is_alive FROM players'
        ' WHERE player_id = ?',
        (player_id,)
    ).fetchone()[0]

    #check if player is Alive
    if str(is_alive) == str(1):
        return (internal_error(9), 400)


    #remove them from the game
    db.execute(
        'DELETE FROM players'
        ' WHERE player_id = ?',
        (player_id, )
    )
    db.commit()

    return jsonify({'message' : 'success'}), 200
