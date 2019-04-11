import pytest
from flask import session
from assassin_server.db import get_db, row_to_dict


#For this test we'll run the example game in the TeX document
def test_mock_game(client, app):
    # We'll let Analeidi create the game
    response=client.post(
        '/creator_access/create_game',
        json={'game_name':'Example Game', 'game_rules':'Example Rules'}
    )

    json_data=response.get_json()
    game_code=json_data['game_code']
    assert 1000 <= game_code and game_code < 10000

    with app.app_context():
        assert get_db().execute(
            'SELECT * FROM games WHERE game_code = ?',
            (game_code,)
        ).fetchone() is not None

    # Now we'll add Analeidi to the game
    add_player_assertions(client, app, 'Analeidi', 'Barrera', 1, game_code)

    # Now we'll add Ellen, Corey, then Jacob to the game
    add_player_assertions(client, app, 'Ellen', 'Graham', 0, game_code)
    add_player_assertions(client, app, 'Corey', 'Pieper', 0, game_code)
    add_player_assertions(client, app, 'Jacob', 'Weightman', 0, game_code)

    # Now we'll start the game!
    # Note that the targets are randomly generated and will be different from the example
    creator_id = None
    with app.app_context():
        creator_id=get_db().execute(
            'SELECT player_id FROM players'
            ' WHERE player_first_name = ? AND player_last_name = ? AND game_code = ?',
            ('Analeidi', 'Barrera', game_code)
        ).fetchone()[0]

    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['this_player_id'] = creator_id

        response = c.get('/creator_access/start_hunt')
        assert response.status_code == 200

    #make sure game_state changed
    with app.app_context():
        assert get_db().execute(
            'SELECT game_state FROM games WHERE game_code = ?',
            (game_code, )
        ).fetchone()[0] == 1

    #make sure each player has a target, and that the targeting function has cycle length 4
    with app.app_context():
        current_id=creator_id
        for i in range(4):
            target_id = get_db().execute(
                'SELECT target_id FROM players WHERE player_id = ?',
                (current_id,)
            ).fetchone()[0]

            assert target_id is not None
            if i < 3:
                assert target_id is not None and target_id != creator_id
            else:
                assert target_id == creator_id
            current_id=target_id

    # Start getting players
    # First we'll let Analeidi get her target
    next_getter = got_target_new_target(app, creator_id)

    #Then we'll let Analeidi's new target get their target
    next_getter = got_target_new_target(app, next_getter)

    #make sure the target of Analeidi's target is Analeidi
    assert next_getter == creator_id

    #find out who Analeidi's last target is:
    last_target_id=None
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['this_player_id']=creator_id

        response=c.get('/player_access/request_target')
        last_target_id=response.get_json()['target_id']

    # We'll let Analeidi win the game
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['this_player_id']=creator_id

        response = c.get('/player_access/got_target')
        assert response.status_code == 302

    #Remove Analeidi's last target
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['this_player_id']=last_target_id

        response=c.get('/player_access/remove_from_game')
        assert response.status_code == 200

    #Make sure they're removed
    with app.app_context():
        assert get_db().execute(
            'SELECT * FROM players'
            ' WHERE player_id = ?',
            (last_target_id, )
        ).fetchone() is None

    #Now Analeidi tells the game to remove her
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['this_player_id']=creator_id

        response=c.get('/player_access/remove_from_game')
        assert response.status_code == 200

    #Make sure both she and the game are deleted
    with app.app_context():
        assert get_db().execute(
            'SELECT * FROM players'
            ' WHERE player_id = ?',
            (creator_id, )
        ).fetchone() is None

        assert get_db().execute(
            'SELECT * FROM games'
            ' WHERE game_code = ?',
            (game_code, )
        ).fetchone() is None

# Get's the target of a player and returns their new target's id
def got_target_new_target(app, getter_id):

    target_id=None
    with app.app_context():
        target_id=get_db().execute(
            'SELECT target_id FROM players'
            ' WHERE player_id = ?',
            (getter_id,)
        ).fetchone()[0]

    new_target_id=None
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['this_player_id'] = getter_id

        response = c.get('/player_access/got_target')
        assert response.status_code == 200
        response = c.get('/player_access/request_target')
        assert response.status_code == 200
        new_target_id = response.get_json()['target_id']

    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['this_player_id']=target_id

        response=c.get('/player_access/remove_from_game')
        assert response.status_code == 200

    with app.app_context():
        assert get_db().execute(
            'SELECT * FROM players'
            ' WHERE player_id = ?',
            (target_id, )
        ).fetchone() is None

    return new_target_id

def add_player_assertions(client, app, player_first_name, player_last_name,is_creator, game_code):
    #get the target info so we can let them remove themselves from the game


    response= client.post(
        '/player_access/add_player',
        json= {
            'player_first_name':player_first_name,
            'player_last_name': player_last_name,
            'is_creator':is_creator,
            'game_code':game_code
        }
    )



    assert response.status_code  == 200
    with app.app_context():
        assert get_db().execute(
            'SELECT * FROM players'
            ' WHERE player_first_name = ? AND player_last_name = ? AND game_code = ?',
            (player_first_name, player_last_name, game_code)
        ).fetchone() is not None
