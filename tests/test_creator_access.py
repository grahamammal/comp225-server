import pytest
import re
import random
import string
from flask import session
from assassin_server.db import get_db


@pytest.mark.parametrize(('game_name', 'game_rules', 'expected_error_id', 'expected_status_code'), (
    (None, 'rules', 7, 400),
    ('name', None, None, 200),
    ('name', 'rules', None, 200),
))
def test_create_game(client, game_name, game_rules, expected_error_id, expected_status_code):



    response = client.post(
        '/creator_access/create_game',
        json={'game_name': game_name, 'game_rules': game_rules}
    )

    assert response.status_code==expected_status_code
    if expected_error_id is not None:
        assert response.get_json()['error_id'] == expected_error_id
    else:
        json_data=response.get_json()
        assert 1000<=json_data['game_code'] and json_data['game_code']<10000

@pytest.mark.parametrize(('num_players', 'is_creator_last', 'expected_error_id', 'expected_status_code'), (
    (10, True, None, 200),
    (10, False, 6, 403),
    (1, True, None, 302),
    (1, False, 6, 403),
    (0, True, 4, 403),
    (0, False, 4, 403),
))
def test_start_hunt(client, num_players, is_creator_last, expected_error_id, expected_status_code):

    for i in range(num_players):
        if i+1 == num_players and is_creator_last:
            generate_player(client, True)
        else:
            generate_player(client, False)

    response=client.get('/creator_access/start_hunt')

    assert response.status_code==expected_status_code
    if expected_error_id is not None:
        assert response.get_json()['error_id']==expected_error_id

def generate_player(client, is_creator):

    rand_first_name = ''.join([random.choice(string.ascii_letters) for n in range(10)])
    rand_last_name = ''.join([random.choice(string.ascii_letters) for n in range(10)])
    client.post(
        '/player_access/add_player',
        json={'player_first_name':rand_first_name,
              'player_last_name':rand_last_name,
              'is_creator':is_creator,
              'game_code': 9999}
    )

def test_max_games(client, app):
    with app.app_context():
        db=get_db()
        for i in range(1003, 9999):
            db.execute(
                'INSERT INTO games (game_name, game_rules, game_code, game_state)'
                ' VALUES (?, ?, ?, ?)',
                ('name', 'rules', i, 0)
            )

        db.commit()
    for i in range(5):
        response=client.post(
            '/creator_access/create_game',
            json={'game_name':'name', 'game_rules':'rules'}
        )

    assert response.status_code==500
    assert response.get_json()['error_id']==8
