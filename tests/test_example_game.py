import pytest
from flask import session
from conftest import create_test_game
from assassin_server.db_models import Players, Games, db, table_to_dict


#For this test we'll run a 10 person game
def test_mock_game(client, app):
    game_size = 10
    # Now we'll start the game!
    players_info = create_test_game(client, game_size, 1)

    game_code = None
    with app.app_context():
        game_code = db.session.query(
                Players.game_code
            ).filter_by(
                player_first_name = players_info[0]['player_first_name']
            ).first().game_code

    creator_id = None
    with app.app_context():
        creator_id = db.session.query(
                Players.player_id
            ).filter_by(
                player_first_name = players_info[0]['player_first_name']
            ).first().player_id

        assert isinstance(creator_id, int)

    #make sure each player has a target, and that the targeting function has cycle length 4
    with app.app_context():
        current_id = creator_id
        for i in range(game_size):
            target_id = db.session.query(
                    Players.target_id
                ).filter_by(
                    player_id = current_id
                ).first().target_id

            assert target_id is not None
            if i < game_size-1:
                assert target_id is not None and target_id != creator_id
            else:
                assert target_id == creator_id
            current_id=target_id

    # start getting players
    # first we'll the first player get their target
    dead_player_index = player_got_target(app, client, players_info, 0, False)

    # now we'll find the index of a player other than the first who is alive. We'll let them win
    winner_index = None
    for i in range(1, game_size):
        if i != dead_player_index:
            winner_index = i

    # find the number of players left
    num_players_alive = None
    with app.app_context():
        num_players_alive = len(
            db.session.query(
                Players.player_id
            ).filter_by(
                game_code = game_code
            ).all()
        )

    assert num_players_alive > 0

    # kill all the other players
    for i in range(num_players_alive-1):
        if i == num_players_alive-2:
            player_got_target(app, client, players_info, winner_index, True)
        else:
            player_got_target(app, client, players_info, winner_index, False)

    # make sure there's 1 player left
    with app.app_context():
        num_players_alive = len(
            db.session.query(
                Players.player_id
            ).filter_by(
                game_code = game_code
            ).all()
        )

        assert num_players_alive == 1

    # finally the winner asks to be removed from the game
    headers = {'Authorization' : 'Bearer ' + players_info[winner_index]['access_token']}
    response=client.get(
        '/player_access/remove_from_game',
        headers=headers
    )
    assert response.status_code == 200

    #Make sure both the winner and the game are deleted
    with app.app_context():
        assert db.session.query(
            Players.player_id
        ).filter_by(
            player_first_name = players_info[winner_index]['player_first_name']
        ).scalar() is None

        assert db.session.query(
            Players.player_id
        ).filter_by(
            game_code = game_code
        ).scalar() is None

        assert db.session.query(
            Games.game_id
        ).filter_by(
            game_code = game_code
        ).scalar() is None


# get's the target of a player and returns their new target's id
def player_got_target(app, client, players_info, getter_index, is_winning_got):

    headers = {'Authorization' : 'Bearer ' + players_info[getter_index]['access_token']}
    response=client.get(
        '/player_access/request_target',
        headers=headers
    )
    target_name = response.get_json()
    assert response.status_code == 200

    target_index = None
    for i in range(len(players_info)):
        if players_info[i]['player_first_name'] == target_name['target_first_name']:
            target_index = i

    target_kill_code = db.session.query(
            Players.player_kill_code
        ).filter_by(
            player_first_name = players_info[target_index]['player_first_name']
        ).first().player_kill_code

    #get your target
    headers=headers = {'Authorization' : 'Bearer ' + players_info[getter_index]['access_token']}
    response=client.post(
        '/player_access/got_target',
        headers=headers,
        json={'guessed_target_kill_code' : target_kill_code}
    )

    assert response.status_code == 200

    assert response.get_json().get('win') == is_winning_got

    headers = {'Authorization' : 'Bearer ' + players_info[target_index]['access_token']}
    response=client.get(
        '/player_access/remove_from_game',
        headers=headers
    )
    assert response.status_code == 200

    # make sure the target was killed and removed
    with app.app_context():
        assert db.session.query(
                Players.player_id
            ).filter_by(
                player_first_name =target_name['target_first_name']
            ).scalar() is None

        assert db.session.query(
                Players.target_first_name
            ).filter_by(
                player_first_name = players_info[getter_index]['player_first_name']
            ).first().target_first_name != target_name['target_first_name']

    return target_index


# In this game, the other player quits from a 2 person game
def test_quitter_game(app, client):
    players_info = create_test_game(client, 2, 1)

    # we'll find the game code
    game_code = None
    with app.app_context():
        game_code = db.session.query(
            Players.game_code
        ).filter_by(
            player_first_name = players_info[0]['player_first_name']
        ).first().game_code

    # we'll make the creator quit
    headers = {'Authorization' : 'Bearer ' + players_info[0]['access_token']}
    response=client.get(
        '/player_access/quit_game',
        headers=headers
    )
    assert response.status_code == 200

    # make sure they're gone
    with app.app_context():
        assert db.session.query(
            Players.player_id
        ).filter_by(
            player_first_name = players_info[0]['player_first_name']
        ).scalar() is None

    assert response.status_code == 200

    # then the other player will check the game status
    response = client.post(
        '/status_access/game_state',
        json={
        'game_code':game_code
        }
    )
    assert response.status_code == 200


    assert response.get_json().get('game_state') == 2

    # make sure there's 1 player left
    with app.app_context():
        num_players_alive = len(
            db.session.query(
                Players.player_id
            ).filter_by(
                game_code = game_code
            ).all()
        )

    assert num_players_alive == 1

    # now the winner asks to be removed from the game
    headers = {'Authorization' : 'Bearer ' + players_info[1]['access_token']}
    response=client.get(
        '/player_access/remove_from_game',
        headers=headers
    )
    assert response.status_code == 200

    # make sure both the winner and the game are deleted
    with app.app_context():
        assert db.session.query(
            Players.player_id
        ).filter_by(
            player_first_name = players_info[1]['player_first_name']
        ).scalar() is None

        assert db.session.query(
            Players.player_id
        ).filter_by(
            game_code = game_code
        ).scalar() is None

        assert db.session.query(
            Games.game_id
        ).filter_by(
            game_code = game_code
        ).scalar() is None
