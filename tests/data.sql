INSERT INTO players (
                      player_kill_code, player_first_name, player_last_name,
                      target_id, target_first_name, target_last_name,
                      is_alive, is_creator, disputed_got,
                      game_code
                    )
VALUES
  (
      1001, "test1", "test1",
      3, "test3", "test3",
      1, 1, 0,
      1000
  ),
  (
      1002, "test2", "test2",
      1, "test1", "test1",
      1, 1, 0,
      1000
  ),
  (
      1003, "test3", "test3",
      2, "test2", "test2",
      1, 1, 0,
      1000
  ),
  (
      null, "test4", "test4",
      null, null, null,
      1, 1, 0,
      1001
  ),
  (
      1005, "test5", "test5",
      6, "test6", "test6",
      1, 1, 0,
      1002
  ),
  (
      1006, "test6", "test6",
      5, "test5", "test5",
      1, 0, 0,
      1002
  ),
  (
      null, "test7", "test7",
      null, null, null,
      0, 0, 0,
      1001
  );


INSERT INTO games (game_name, game_rules, game_code, game_state)
VALUES
  ("test_game", "no rules dweeb", 1000, 1),
  ("player_access_test_game", null, 1001, 0),
  ("player_access_test_got", "nope", 1002, 1),
  ("another_test_game", "still no rules dweeb", 9999, 0);
