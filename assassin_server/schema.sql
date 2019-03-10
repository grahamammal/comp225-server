DROP TABLE IF EXISTS players;
DROP TABLE IF EXISTS games;

CREATE TABLE players (
  player_id INTEGER PRIMARY KEY AUTOINCREMENT,
  player_name TEXT NOT NULL,
  target_name TEXT,
  is_alive BOOLEAN,
  disputed_Got BOOLEAN,
  game_code INTEGER NOT NULL
);

CREATE TABLE games (
  game_id INTEGER PRIMARY KEY AUTOINCREMENT,
  game_name TEXT NOT NULL,
  game_code INTEGER UNIQUE NOT NULL,
  game_state INTEGER NOT NULL
);
