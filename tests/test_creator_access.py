import pytest
import re
import random
import string
from flask import session
from assassin_server.db import get_db


@pytest.mark.parametrize(
    ('game_name', 'game_rules', 'expected_error_id', 'expected_status_code'),
    (
        (None, 'rules', 7, 400), # there is no game name
        ('name', None, None, 200), # there are no game rules
        ('name', 'rules', None, 200), #there are both rules and a name
    )
)
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

@pytest.mark.parametrize(
    ('num_players', 'is_creator', 'player_id', 'expected_error_id', 'expected_status_code'),
    (
        (10, True, 18, None, 200), # the creator tries to start a 10 person hunt
        (10, False, 18, 6, 403), # a player other than the creator tries to start a 10 person hunt
        (1, True, 9, None, 302), # the creator tries to start a 1 person hunt
        (1, False, 9, 6, 403), # a player other than the creator tries to start a 1 person hunt
        (0, True, 100, 4, 403), # a creator that doesn't exist tries to start a hunt
        (0, False, 100, 4, 403), # a player that doesn't exist tries to start a hunt
    )
)
def test_start_hunt(client, num_players, is_creator, player_id, expected_error_id, expected_status_code):

    for i in range(num_players):
        if i+1 == num_players and is_creator:
            generate_player(client, True)
        else:
            generate_player(client, False)

    response=client.post(
        '/creator_access/start_hunt',
        json={'player_id' : player_id}
    )

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
        for i in range(1004, 9999):
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


@pytest.mark.parametrize(
    ('this_player_id', 'expected_length', 'expected_error_id', 'expected_status_code'),
    (
        (8, 1, None, 200), # there is only 1 player in the game
        (1, 3, None, 200), # there are 3 players in the game
        (2, None, 6, 403), # the player asking isn't the creator
        (100, None, 4, 403) # the player asking doesn't exist
    )
)
def test_player_list(app, client, this_player_id, expected_length, expected_error_id, expected_status_code):
    response = client.post(
        '/creator_access/player_list',
        json={'player_id' : this_player_id}
    )

    assert response.status_code == expected_status_code

    if expected_error_id is None:
        assert len(response.get_json()['players']) == expected_length
    else:
        assert response.get_json()['error_id'] == expected_error_id
