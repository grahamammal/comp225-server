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
    ('this_player_id','expected_error_id','expected_status_code'),
    (
        (None, 4, 403), # no such player
        (4, 5, 400), # player has no target
        (5, None, 302), # player wins
        (1, None, 200), # player got target but didn't win
    )
)
def test_got_target(app, this_player_id, expected_error_id, expected_status_code):

    with app.test_client() as c:
        if this_player_id is not None:
            with c.session_transaction() as sess:
                sess['this_player_id'] = this_player_id

        response = c.get('/player_access/got_target')
        assert response.status_code==expected_status_code
        if expected_error_id is not None:
            assert response.get_json()['error_id']==expected_error_id

def test_won_game(client):
    response=client.get('/player_access/won_game')

@pytest.mark.parametrize(
    ('game_code', 'expected_rules', 'expected_name'),
    (
        (1000, 'no rules dweeb', 'test_game'),
        (1001, None, 'player_access_test_game'),
    )
)
def test_get_game_info(client, game_code, expected_rules, expected_name):
    response= client.post(
        '/player_access/get_game_rules',
        json={"game_code":game_code}
    )

    json_data=response.get_json()
    assert json_data['game_rules'] == expected_rules


@pytest.mark.parametrize(
    ('this_player_id','expected_error_id', 'expected_status_code'),
    (
        (None, 4, 403),
        (4, 5, 400),
        (1, None, 200)
    )
)
def test_request_target(app, this_player_id, expected_error_id,expected_status_code):
    with app.test_client() as c:
        if this_player_id is not None:
            with c.session_transaction() as sess:
                sess['this_player_id']=this_player_id
        response=c.get('/player_access/request_target')

        assert response.status_code == expected_status_code
        if expected_error_id is not None:
            assert response.get_json()['error_id']==expected_error_id
        else:
            assert response.get_json()['target_id']==2
