import pytest
from flask import session
from conftest import create_test_game

@pytest.mark.parametrize(
    ('expected_is_alive', 'expected_error_id', 'expected_status_code'),
    (
        (0, None, 200), # a dead player asks for their status
        (1, None, 200), # an alive player asks for their status
        (None, 12, 422), # a non existent player asks for their status
    )
)
def test_is_alive(app, client, expected_is_alive, expected_error_id, expected_status_code):

    if expected_is_alive is not None:
        players_info = create_test_game(client, 3, 1)

        # set player to dead or alive
        with app.app_context():
            player = db.session.query(
                    Players
                ).filter_by(
                    player_first_name = players_info[0]['player_first_name'],
                    player_last_name = players_info[0]['player_last_name']
                ).first()

            player.is_alive = (1 == True)
            db.session.commit()

        # send our request
        headers=headers = {'Authorization' : 'Bearer ' + players_info[0]['access_token']}
        response=client.get(
            '/status_access/is_alive',
            headers=headers
        )
    else:
        headers=headers = {'Authorization' : 'Bearer ' + 'dyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1NTU2MjA3MTMsIm5iZiI6MTU1NTYyMDcxMywianRpIjoiZTc1YTU5MzEtODU2Yy00OTcwLThiZmItNDRhMWU2OTI3OGJiIiwiZXhwIjoxNTU1NjIxNjEzLCJpZGVudGl0eSI6NSwiZnJlc2giOmZhbHNlLCJ0eXBlIjoiYWNjZXNzIn0.4lpagzD_gVJqWWXW37CkzuccHYoMtjVOQ7j08SXbb_0'}
        response=client.get(
            '/status_access/is_alive',
            headers=headers
        )
    assert response.status_code == expected_status_code

    assert response.get_json().get('error_id') == expected_error_id
    assert response.get_json().get('is_alive') == expected_is_alive


@pytest.mark.parametrize(
    ('game_code', 'expected_game_state', 'expected_error_id', 'expected_status_code'),
    (
        (1000, 1, None, 200),
        (1001, 0, None, 200),
        (5000, None, 5, 400),
        (1003, 2, None, 200)
    )
)
def test_game_state(client, game_code, expected_game_state, expected_error_id, expected_status_code):
    response=client.post(
        '/status_access/game_state',
        json={
              'game_code':game_code
        }
     )

    assert response.status_code==expected_status_code

    if expected_error_id is not None:
        assert response.get_json()['error_id']==expected_error_id
    else:
        assert response.get_json()['game_state']==expected_game_state
