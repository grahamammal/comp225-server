INSERT INTO players (
                                 player_first_name, player_last_name,
                      target_id, target_first_name, target_last_name,
                      is_alive, is_creator, disputed_got,
                      game_code
                    )
VALUES
  (
       "test1", "test1",
    2, "test3", "test3",
    1, 1, 0,
    1000
  ),
  (
       "test2", "test2",
    0, "test1", "test1",
    1, 1, 0,
    1000
  ),
  (
       "test3", "test3",
    1, "test2", "test2",
    1, 1, 0,
    1000
  );

INSERT INTO games (game_name, game_rules, game_code, game_state)
VALUES
  ("test_game", "no rules dweeb", 1000, 1),
  ("another_test_game", "still no rules dweeb", 9999, 0);
