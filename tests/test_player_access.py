import pytest
from flask import session
from assassin_server.db import get_db
from conftest import create_test_game

@pytest.mark.parametrize(
    ('player_first_name', 'player_last_name',
     'is_creator', 'game_code',
     'expected_error_id',
     'expected_status_code'),
    (
        ('add1', 'test', 0, 9999, None, 200),#valid
        ('test4', 'test4', 0, 1001, 2, 400),#player already exists
        ('add2', 'test', 0, 0, 0, 400),#game doesn't exist
        ('add3', 'test', 0, 1000, 1, 400),#game already started
        ('add4', 'test', 1, 1001, 3, 400),#creator already exists
    )
)
def test_add_player(client,
                    player_first_name, player_last_name,
                    is_creator, game_code,
                    expected_error_id,
                    expected_status_code):
    response=client.post(
        '/player_access/add_player',
        json={'player_first_name':player_first_name,
              'player_last_name':player_last_name,
              'is_creator':is_creator,
              'game_code':game_code}
    )

    assert response.status_code==expected_status_code
    if expected_error_id is not None:
        assert response.get_json()['error_id']==expected_error_id

@pytest.mark.parametrize(
    ('num_players', 'game_state', 'player_is_alive', 'guessed_correct', 'expected_error_id','expected_status_code'),
    (
        (3, 0, True, None, 5, 400), # player has no target
        (2, 1, True, True, None, 302), # player wins
        (3, 1, True, True, None, 200), # player got target but didn't win
        (3, 1, False, None, 9, 400), # player is dead
        (3, 1, True, False, 10, 400), # player gave wrong kill code
        (None, None, None, None, None, 401) # player doesn't exist
    )
)
def test_got_target(app, client, num_players, game_state, player_is_alive, guessed_correct, expected_error_id, expected_status_code):

    if num_players is None:
        # send fake authorization
        headers=headers = {'Authorization' : 'Bearer ' + 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1NTU2MjA3MTMsIm5iZiI6MTU1NTYyMDcxMywianRpIjoiZTc1YTU5MzEtODU2Yy00OTcwLThiZmItNDRhMWU2OTI3OGJiIiwiZXhwIjoxNTU1NjIxNjEzLCJpZGVudGl0eSI6NSwiZnJlc2giOmZhbHNlLCJ0eXBlIjoiYWNjZXNzIn0.4lpagzD_gVJqWWXW37CkzuccHYoMtjVOQ7j08SXbb_0'}
        response=client.post(
            '/player_access/got_target',
            headers=headers,
            json={'guessed_target_kill_code' : 1234}
        )
    else:
        players_info = create_test_game(client, num_players, game_state)

        target_kill_code = None
        # if the game is started, find the target
        if game_state == 1:
            with app.app_context():
                target_id=get_db().execute(
                    'SELECT target_id FROM players'
                    ' WHERE player_first_name = ? AND player_last_name = ?',
                    (players_info[0]['player_first_name'], players_info[0]['player_last_name'])
                ).fetchone()[0]

                target_kill_code=get_db().execute(
                    'SELECT player_kill_code FROM players'
                    ' WHERE player_id = ?',
                    (target_id, )
                ).fetchone()[0]

        # if the player should be dead force them to die
        if not player_is_alive:
            with app.app_context():
                get_db().execute(
                    'UPDATE players'
                    ' SET is_alive = 0'
                    ' WHERE player_first_name = ? AND player_last_name = ?',
                    (players_info[0]['player_first_name'], players_info[0]['player_last_name'])
                )
                get_db().commit()

        if not guessed_correct:
            # send the wrong kill code
            headers=headers = {'Authorization' : 'Bearer ' + players_info[0]['access_token']}
            response=client.post(
                '/player_access/got_target',
                headers=headers,
                json={'guessed_target_kill_code' : 1234}
            )
        else:
            # send the correct kill code
            headers=headers = {'Authorization' : 'Bearer ' + players_info[0]['access_token']}
            response=client.post(
                '/player_access/got_target',
                headers=headers,
                json={'guessed_target_kill_code' : target_kill_code}
            )

    assert response.status_code==expected_status_code
    assert response.get_json().get('error_id')==expected_error_id

def test_won_game(client):
    response=client.get('/player_access/won_game')
    assert response.status_code==200

@pytest.mark.parametrize(
    ('game_code', 'expected_rules', 'expected_name', 'expected_status_code'),
    (
        (1000, 'no rules dweeb', 'test_game', 200),
        (1001, None, 'player_access_test_game', 200),
        (5000, None, None, 400)
    )
)
def test_get_game_info(client, game_code, expected_rules, expected_name, expected_status_code):
    response= client.post(
        '/player_access/get_game_info',
        json={"game_code":game_code}
    )

    json_data=response.get_json()
    if expected_status_code==200:
        assert json_data['game_rules'] == expected_rules
        assert json_data['game_name'] == expected_name

    assert response.status_code==expected_status_code

@pytest.mark.parametrize(
    ('game_state', 'expected_error_id', 'expected_status_code'),
    (
        (0, 5, 400), # this player's game has not started
        (1, None, 200), # the player is valid
        (None, None, 401) # the player doesn't exist
    )
)
def test_request_target(app, client, game_state, expected_error_id, expected_status_code):

    if game_state is None:
        # send fake info if the player doesn't exist
        headers=headers = {'Authorization' : 'Bearer ' + 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1NTU2MjA3MTMsIm5iZiI6MTU1NTYyMDcxMywianRpIjoiZTc1YTU5MzEtODU2Yy00OTcwLThiZmItNDRhMWU2OTI3OGJiIiwiZXhwIjoxNTU1NjIxNjEzLCJpZGVudGl0eSI6NSwiZnJlc2giOmZhbHNlLCJ0eXBlIjoiYWNjZXNzIn0.4lpagzD_gVJqWWXW37CkzuccHYoMtjVOQ7j08SXbb_0'}
        response=client.get(
            '/player_access/request_target',
            headers=headers
        )
    else:
        # create a test game
        players_info = create_test_game(client, 3, game_state)

        headers = {'Authorization' : 'Bearer ' + players_info[0]['access_token']}
        response=client.get(
            '/player_access/request_target',
            headers=headers
        )

    assert response.status_code == expected_status_code
    assert response.get_json().get('error_id') == expected_error_id

    # if we expect a target
    if expected_status_code is 200:
        assert response.get_json().get('target_first_name') is not None
        assert response.get_json().get('target_last_name') is not None


@pytest.mark.parametrize(
    ('game_state', 'expected_error_id', 'expected_status_code'),
    (
        (1, None, 200), # player has a kill code
        (None, None, 401), # player doesn't exist
    )
)
def test_request_kill_code(client, game_state, expected_error_id, expected_status_code):
    if game_state is None:
        # send fake info if the player doesn't exist
        headers=headers = {'Authorization' : 'Bearer ' + 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1NTU2MjA3MTMsIm5iZiI6MTU1NTYyMDcxMywianRpIjoiZTc1YTU5MzEtODU2Yy00OTcwLThiZmItNDRhMWU2OTI3OGJiIiwiZXhwIjoxNTU1NjIxNjEzLCJpZGVudGl0eSI6NSwiZnJlc2giOmZhbHNlLCJ0eXBlIjoiYWNjZXNzIn0.4lpagzD_gVJqWWXW37CkzuccHYoMtjVOQ7j08SXbb_0'}
        response=client.get(
            '/player_access/request_kill_code',
            headers=headers
        )
    else:
        # create a test game
        players_info = create_test_game(client, 3, game_state)

        headers = {'Authorization' : 'Bearer ' + players_info[0]['access_token']}
        response=client.get(
            '/player_access/request_kill_code',
            headers=headers
        )

    assert response.status_code == expected_status_code
    assert response.get_json().get('error_id') == expected_error_id

    # if we expect a target
    if expected_status_code is 200:
        assert response.get_json().get('player_kill_code') is not None

@pytest.mark.parametrize(
    ('num_players', 'is_alive', 'expected_error_id', 'expected_status_code'),
    (
        (3, False, None, 200), # the player is dead and should be removed
        (1, True, None, 200), # the player is the last player of the game and the game should be deleted
        (3, True, 9, 400), # the player is alive and shouldn't be removed
        (None, None, None, 401), # the player doesn't exist
    )
)
def test_remove_from_game(app, client, num_players, is_alive, expected_error_id, expected_status_code):

    if num_players is None:
        # send fake info if the player doesn't exist
        headers=headers = {'Authorization' : 'Bearer ' + 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1NTU2MjA3MTMsIm5iZiI6MTU1NTYyMDcxMywianRpIjoiZTc1YTU5MzEtODU2Yy00OTcwLThiZmItNDRhMWU2OTI3OGJiIiwiZXhwIjoxNTU1NjIxNjEzLCJpZGVudGl0eSI6NSwiZnJlc2giOmZhbHNlLCJ0eXBlIjoiYWNjZXNzIn0.4lpagzD_gVJqWWXW37CkzuccHYoMtjVOQ7j08SXbb_0'}
        response=client.get(
            '/player_access/request_kill_code',
            headers=headers
        )

    else:
        # create a test game
        players_info = create_test_game(client, num_players, 1)

        if not is_alive:
        # force dead players to be dead
            with app.app_context():
                get_db().execute(
                    'UPDATE players'
                    ' SET is_alive = 0'
                    ' WHERE player_first_name = ? AND player_last_name = ?',
                    (players_info[0]['player_first_name'], players_info[0]['player_last_name'])
                )
                get_db().commit()

        headers = {'Authorization' : 'Bearer ' + players_info[0]['access_token']}
        response=client.get(
            '/player_access/remove_from_game',
            headers=headers
        )

    assert response.status_code == expected_status_code
    assert response.get_json().get('error_id') == expected_error_id
