import pytest
import re
import random
import string
from flask import session

from assassin_server.db import get_db
from conftest import create_test_game

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
    ('num_players', 'is_creator', 'expected_error_id', 'expected_status_code'),
    (
        (10, True, None, 200), # the creator tries to start a 10 person hunt
        (10, False, 6, 403), # a player other than the creator tries to start a 10 person hunt
        (1, True, None, 302), # the creator tries to start a 1 person hunt
        (None, False, 12, 422), # a player that doesn't exist tries to start a hunt
    )
)
def test_start_hunt(client, num_players, is_creator, expected_error_id, expected_status_code):
    if num_players is None:
        headers=headers = {'Authorization' : 'Bearer ' + 'dyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1NTU2MjA3MTMsIm5iZiI6MTU1NTYyMDcxMywianRpIjoiZTc1YTU5MzEtODU2Yy00OTcwLThiZmItNDRhMWU2OTI3OGJiIiwiZXhwIjoxNTU1NjIxNjEzLCJpZGVudGl0eSI6NSwiZnJlc2giOmZhbHNlLCJ0eXBlIjoiYWNjZXNzIn0.4lpagzD_gVJqWWXW37CkzuccHYoMtjVOQ7j08SXbb_0'}
        response=client.get(
            '/creator_access/start_hunt',
            headers=headers
        )

    else:
        players_info=create_test_game(client, num_players, 0)

        if is_creator:
            headers=headers = {'Authorization' : 'Bearer ' + players_info[0]['access_token']}
            response=client.get(
                '/creator_access/start_hunt',
                headers=headers
            )

        else:
            headers=headers = {'Authorization' : 'Bearer ' + players_info[1]['access_token']}
            response=client.get(
                '/creator_access/start_hunt',
                headers=headers
            )

    response_json=response.get_json()

    assert response.status_code==expected_status_code
    assert response.get_json().get('error_id') == expected_error_id

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
    ('num_players', 'is_creator', 'expected_length', 'expected_error_id', 'expected_status_code'),
    (
        (1, True, 1, None, 200), # creator asking, there is only 1 player in the game
        (3, 1, 3, None, 200), # creator asking, there are 3 players in the game
        (3, 0, None, 6, 403), # the player asking isn't the creator
        (None, None, None, 12, 422) # the player asking doesn't exist
    )
)
def test_player_list(client, num_players, is_creator, expected_length, expected_error_id, expected_status_code):
    if num_players is None:
        headers=headers = {'Authorization' : 'Bearer ' + 'dyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1NTU2MjA3MTMsIm5iZiI6MTU1NTYyMDcxMywianRpIjoiZTc1YTU5MzEtODU2Yy00OTcwLThiZmItNDRhMWU2OTI3OGJiIiwiZXhwIjoxNTU1NjIxNjEzLCJpZGVudGl0eSI6NSwiZnJlc2giOmZhbHNlLCJ0eXBlIjoiYWNjZXNzIn0.4lpagzD_gVJqWWXW37CkzuccHYoMtjVOQ7j08SXbb_0'}
        response=client.get(
            '/creator_access/start_hunt',
            headers=headers
        )
    else:
        players_info=create_test_game(client, num_players, 0)

        if is_creator:
            headers=headers = {'Authorization' : 'Bearer ' + players_info[0]['access_token']}
            response=client.get(
                '/creator_access/player_list',
                headers=headers
            )
        else:
            headers=headers = {'Authorization' : 'Bearer ' + players_info[1]['access_token']}
            response=client.get(
                '/creator_access/player_list',
                headers=headers
            )

    assert response.status_code == expected_status_code
    assert response.get_json().get('error_id') == expected_error_id
    if expected_length is not None:
        assert len(response.get_json().get('players')) == expected_length
