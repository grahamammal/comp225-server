import pytest
from flask import session
from assassin_server.db import get_db

#first last iscreator game code
@pytest.mark.parametrize(
    ('player_first_name', 'player_last_name',
     'is_creator', 'game_code',
     'expected_status_code'),
    (
        ('add1', 'test', 0, 9999, 200),#valid
        ('test4', 'test4', 0, 1001, 400),#player already exists
        ('add2', 'test', 0, 0, 400),#game doesn't exist
        ('add3', 'test', 0, 1000, 400),#game already started
        ('add4', 'test', 1, 1001, 400),#creator already exists
    )
)
def test_add_player(client,
                    player_first_name, player_last_name,
                    is_creator, game_code,
                    expected_status_code):
    response=client.post(
        '/player_access/add_player',
        json={'player_first_name':player_first_name,
              'player_last_name':player_last_name,
              'is_creator':is_creator,
              'game_code':game_code}
    )

    assert response.status_code==expected_status_code

@pytest.mark.parametrize(
    ('this_player_id','expected_status_code'),
    (
        (None, 403),
        (3, 400),
        (5, 302),
        (0, 200),
    )
)
def test_got_target(app, this_player_id, expected_status_code):

    with app.test_client() as c:
        if this_player_id is not None:
            with c.session_transaction() as sess:
                sess['this_player_id'] = this_player_id

        response = c.get('/player_access/got_target')
    #assert response.status_code==expected_status_code

def test_won_game(client):
    response=client.get('/player_access/won_game')

@pytest.mark.parametrize(
    ('game_code', 'expected_rules'),
    (
        (1000, 'no rules dweeb'),
        (1001, None),
    )
)
def test_get_game_rules(client, game_code, expected_rules):
    response= client.post(
        '/player_access/get_game_rules',
        json={"game_code":game_code}
    )

    json_data=response.get_json()
    assert json_data['game_rules'] == expected_rules


@pytest.mark.parametrize(
    ('this_player_id','expected_status_code'),
    (
        (None, 403),
        (4, 400),
        (1, 200)
    )
)
def test_request_target(app, this_player_id, expected_status_code):
    with app.test_client() as c:
        if this_player_id is not None:
            with c.session_transaction() as sess:
                sess['this_player_id']=this_player_id
        response=c.get('/player_access/request_target')

        assert response.status_code == expected_status_code
        if this_player_id == 1:
            assert response.get_json()['target_id']==2
