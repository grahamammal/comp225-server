import os
import tempfile

import pytest
from assassin_server import create_app
import pytest
import sqlalchemy as sa
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from pytest_postgresql.factories import (init_postgresql_database,
                                         drop_postgresql_database)
import random

try:
    DB_CONN = os.environ['TEST_DATABASE_URL']
except KeyError:
    raise KeyError('TEST_DATABASE_URL not found. You must export a database ' +
                   'connection string to the environmental variable ' +
                   'TEST_DATABASE_URL in order to run tests.')
else:
    DB_OPTS = sa.engine.url.make_url(DB_CONN).translate_connect_args()

pytest_plugins = ['pytest-flask-sqlalchemy']


@pytest.fixture(scope='session')
def database(request):
    '''
    Create a Postgres database for the tests, and drop it when the tests are done.
    '''
    pg_host = DB_OPTS.get("host")
    pg_port = DB_OPTS.get("port")
    pg_user = DB_OPTS.get("username")
    pg_db = DB_OPTS["database"]


    init_postgresql_database(pg_user, pg_host, pg_port, pg_db)

    @request.addfinalizer
    def drop_database():
        drop_postgresql_database(pg_user, pg_host, pg_port, pg_db, 11.2)


@pytest.fixture(scope = 'session')
def app(database):
    app = create_app({
        'TESTING': True,
    })

    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['TEST_DATABASE_URL']

    yield app

@pytest.fixture(autouse=True)
def enable_transactional_tests(db_session):
    pass

@pytest.fixture(scope='session')
def _db(app, request):
    '''
    Provide the transactional fixtures with access to the database via a Flask-SQLAlchemy
    database connection.
    '''
    db = SQLAlchemy(app)

    setup_db(db)
    return db

@pytest.fixture(scope = 'session')
def client(app):
    return app.test_client()


@pytest.fixture(scope = 'session')
def runner(app):
    return app.test_cli_runner()


def test_tests():
    assert True == True

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

def setup_db(db):
    class Players(db.Model):
        __tablename__ = 'players'

        player_id = db.Column(db.Integer, primary_key = True, autoincrement = True)
        player_kill_code = db.Column(db.Integer)
        player_first_name = db.Column(db.String(50), nullable = False)
        player_last_name = db.Column(db.String(50), nullable = False)

        target_id = db.Column(db.Integer)
        target_first_name = db.Column(db.String(50))
        target_last_name = db.Column(db.String(50))

        is_alive = db.Column(db.Boolean, nullable = False)
        is_creator = db.Column(db.Boolean, nullable = False)

        game_code = db.Column(db.Integer, nullable = False)

        def as_dict(self):
            return {c.name: getattr(self, c.name) for c in self.__table__.columns} # from : https://stackoverflow.com/questions/5022066/how-to-serialize-sqlalchemy-result-to-json

    class Games(db.Model):
        __tablename__ = 'games'
        game_id = db.Column(db.Integer, primary_key = True, autoincrement = True)
        game_name = db.Column(db.String(100), nullable = False)
        game_rules = db.Column(db.String(100))
        game_code = db.Column(db.Integer, unique = True, nullable = False)

        game_state = db.Column(db.Integer, nullable = False)

        def as_dict(self):
            return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    db.create_all()


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
