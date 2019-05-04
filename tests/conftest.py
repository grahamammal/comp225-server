import os
import tempfile

import pytest
from assassin_server import create_app
from assassin_server.__init__ import db

import random




@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
    })

    with app.app_context():
        db.drop_all()
        db.create_all()
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()



def create_test_game(client, num_players, game_state):
    # create the fake game
    create_game_response=client.post(
        '/creator_access/create_game',
        json={
            'game_name' : 'test',
            'game_rules' : 'test'
        }
    )

    # get the game code for our fake game
    game_code=create_game_response.get_json()['game_code']

    # set up our data storage
    players_info = []

    # add the creator first
    creator_info=add_test_player(client, 1, game_code)
    players_info.append(creator_info)

    # add all the non_creators
    for i in range(num_players-1):
        non_creator_info=add_test_player(client, 0, game_code)
        players_info.append(non_creator_info)

    # starts the game if we want to
    if game_state == 1:
        headers = {'Authorization' : 'Bearer ' + creator_info['access_token']}
        start_hunt_response=client.get(
            '/creator_access/start_hunt',
            headers = headers
        )

        assert start_hunt_response.status_code == 200 or start_hunt_response.status_code == 302

    assert len(players_info) == num_players

    return players_info


# adds a player and returns a dictonary of relevant information
def add_test_player(client, is_creator, game_code):
    random_first_name = 'test' + str(random.uniform(0, 10))
    random_last_name = 'test' + str(random.uniform(0, 10))
    add_player_response=client.post(
        '/player_access/add_player',
        json={
            'player_first_name' : random_first_name,
            'player_last_name' : random_last_name,
            'is_creator' : is_creator,
            'game_code' : game_code,
        }
    )

    assert add_player_response.status_code == 200

    player_info=add_player_response.get_json()

    player_info['game_code'] = game_code
    player_info['is_creator'] = is_creator
    player_info['player_first_name'] = random_first_name
    player_info['player_last_name'] = random_last_name

    return player_info
