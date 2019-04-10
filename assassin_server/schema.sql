DROP TABLE IF EXISTS players;
DROP TABLE IF EXISTS games;

CREATE TABLE players (
  player_id INTEGER PRIMARY KEY AUTOINCREMENT,
  player_first_name TEXT NOT NULL,
  player_last_name TEXT NOT NULL,

  target_id INTEGER,
  target_first_name TEXT,
  target_last_name TEXT,

  is_alive BOOLEAN NOT NULL,
  is_creator BOOLEAN NOT NULL,
  disputed_got BOOLEAN NOT NULL,

  game_code INTEGER NOT NULL
);

CREATE TABLE games (
  game_id INTEGER PRIMARY KEY AUTOINCREMENT,

  game_name TEXT NOT NULL,
  game_rules TEXT,
  game_code INTEGER UNIQUE NOT NULL,

  game_state INTEGER NOT NULL
);
