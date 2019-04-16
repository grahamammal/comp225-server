import pytest
from flask import session
from assassin_server.db import get_db

#first last iscreator game code
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
    ('this_player_id','expected_error_id','expected_status_code', 'guessed_target_kill_code'),
    (
        (4, 5, 400, None), # player has no target
        (5, None, 302, 1006), # player wins
        (1, None, 200, 1003), # player got target but didn't win
    )
)
def test_got_target(client, this_player_id, expected_error_id, expected_status_code, guessed_target_kill_code):

        response = client.post(
            '/player_access/got_target',
            json={'player_id' : this_player_id,
                  'guessed_target_kill_code' : guessed_target_kill_code}
        )

        assert response.status_code==expected_status_code
        if expected_error_id is not None:
            assert response.get_json()['error_id']==expected_error_id

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
    ('this_player_id','expected_error_id', 'expected_status_code'),
    (
        (4, 5, 400),
        (1, None, 200)
    )
)
def test_request_target(app, client, this_player_id, expected_error_id, expected_status_code):

        response=client.post(
            '/player_access/request_target',
            json={'player_id':this_player_id}
        )


        assert response.status_code == expected_status_code
        if expected_error_id is not None:
            print(response)
            assert response.get_json()['error_id']==expected_error_id
        else:
            assert response.get_json()['target_first_name'] == 'test3'
            assert response.get_json()['target_last_name'] == 'test3'
