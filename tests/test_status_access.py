import pytest
from flask import session
from assassin_server.db import get_db

@pytest.mark.parametrize(
    ('player_id', 'expected_is_alive', 'expected_error_id', 'expected_status_code'),
    (
        (7, 0, None, 200),
        (1, 1, None, 200),
        (10, None, 4, 403),
        (None, None, 4, 403)
    )
)
def test_is_alive(client, app, player_id, expected_is_alive, expected_error_id, expected_status_code):
    with app.test_client() as c:
        if player_id is not None:
            with c.session_transaction() as sess:
                sess['this_player_id'] = player_id

        response = c.get('/status_access/is_alive')
        assert response.status_code==expected_status_code

        if expected_error_id is not None:
            assert response.get_json()['error_id']==expected_error_id
        else:
            assert response.get_json()['is_alive']==expected_is_alive


@pytest.mark.parametrize(
    ('game_code', 'expected_is_game_state', 'expected_error_id', 'expected_status_code'),
    (
        (1000, 1, None, 200),
        (1001, 0, None, 200),
        (5000, None, 5, 400)
    )
)
def test_is_game_started(client, game_code, expected_is_game_state, expected_error_id, expected_status_code):
    response=client.post(
        '/status_access/is_game_started',
        json={
              'game_code':game_code
        }
     )

    assert response.status_code==expected_status_code

    if expected_error_id is not None:
        assert response.get_json()['error_id']==expected_error_id
    else:
        assert response.get_json()['game_state']==expected_is_game_state
