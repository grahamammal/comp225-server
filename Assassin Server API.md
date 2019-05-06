

# Assassin Server API Docs
_Analeidi Barrera,_
_Ellen Graham,_
_Corey Pieper,_
_Jacob Weightman_

- [Assassin Server API Docs](#assassin-server-api-docs)
  * [Player Requests](#player-requests)
    + [Get Game Info](#get-game-info)
      - [HTTP Request](#http-request)
      - [URL Parameters](#url-parameters)
      - [Return Value](#return-value)
    + [Got Target](#got-target)
      - [HTTP Request](#http-request-1)
      - [URL Parameters](#url-parameters-1)
      - [Return Value](#return-value-1)
    + [Add Player](#add-player)
      - [HTTP Request](#http-request-3)
      - [URL Parameters](#url-parameters-3)
      - [Return Value](#return-value-3)
    + [Request Target](#request-target)
      - [HTTP Request](#http-request-4)
      - [URL Parameters](#url-parameters-4)
      - [Return Value](#return-value-4)
    + [Request Kill Code](#request-kill-code)
      - [HTTP Request](#http-request-5)
      - [URL Parameters](#url-parameters-5)
      - [Return Value](#return-value-5)
    + [Remove From Game](#remove-from-game)
      - [HTTP Request](#http-request-6)
      - [URL Parameters](#url-parameters-6)
      - [Return Value](#return-value-6)
    + [Quit Game](#get-game-info)
      - [HTTP Request](#http-request)
      - [URL Parameters](#url-parameters)
      - [Return Value](#return-value)
  * [Game Creator Requests](#game-creator-requests)
    + [Create Game](#create-game)
      - [HTTP Request](#http-request-7)
      - [URL Parameters](#url-parameters-7)
      - [Return Value](#return-value-7)
    + [Start Hunt](#start-hunt)
      - [HTTP Request](#http-request-8)
      - [URL Parameters](#url-parameters-8)
        * [Return Value](#return-value-8)
    + [Player List](#player-list)
      - [HTTP Request](#http-request-9)
      - [URL Parameters](#url-parameters-9)
        * [Return Value](#return-value-9)
  * [Status Requests](#status-requests)
    + [Is Alive](#is-alive)
      - [HTTP Request](#http-request-10)
      - [URL Parameters](#url-parameters-10)
      - [Return Value](#return-value-10)
    + [Game State](#is-game-started)
      - [HTTP Request](#http-request-11)
      - [URL Parameters](#url-parameters-11)
      - [Return Value](#return-value-11)
  * [Debug Requests](#debug-requests)
    + [Get Player](#get-player)
      - [HTTP Request](#http-request-12)
      - [URL Parameters](#url-parameters-12)
      - [Return Value](#return-value-12)
    + [Get All Players](#get-all-players)
      - [HTTP Request](#http-request-13)
      - [URL Parameters](#url-parameters-13)
      - [Return Value](#return-value-13)
    + [Get Game](#get-game)
      - [HTTP Request](#http-request-14)
      - [URL Parameters](#url-parameters-14)
      - [Return Value](#return-value-14)
    + [Get All Games](#get-all-games)
      - [HTTP Request](#http-request-15)
      - [URL Parameters](#url-parameters-15)
      - [Return Value](#return-value-15)
  * [Errors](#errors)

## Player Requests

### Get Game Info

This endpoint will return the game name and rules of the specified game

#### HTTP Request
---
```
POST http://<localhost>/player_access/get_game_info
    {
        "game_code": 9999
    }
```

#### URL Parameters
---
| Parameter | Default | Description
| ------ | ------ | ------|
| game_code | None | The 4 digit code of the game you want the rules of |

#### Return Value
---
```
{
	"game_rules": "rules"
	"game_name": "name"
}
```
### Got Target

This endpoint remove your target from the game and provide you with a new one. Will return ```win: true``` if the game is won,  ```win: false``` otherwise.


#### HTTP Request
---
```
POST http://<localhost>/player_access/got_target
	headers: Authorization: "Bearer dyJ0eXAiOiJKV1Q..."
    {
        "guessed_target_kill_code" = 1234
    }
```

#### URL Parameters
---
| Parameter | Default | Description
| ------ | ------ | ------|
| guessed\_target\_kill\_code | None | The kill code of the player you got |

#### Return Value
```
{
	"win": true
}
```


### Add Player

This endpoint will add a player to a game.

#### HTTP Request
---
```
POST http://<localhost>/player_access/add_player  
    {
        "player_first_name": "example"
        "player_last_name": "example"
        "is_creator": false
        "game_code": 9999
    }
```

#### URL Parameters
---
| Parameter | Default | Description
| ------ | ------ | ------|
| player\_first\_name | None | The first name of the player |
| player\_last\_name | None | The last name of the player |
| is_creator | None | true if the player created the game, false otherwise |
| game_code | None | The 4 digit code of the game the player is joining |

#### Return Value
---
```
{
    "access_token" : "dyJ0eXAiOiJKV1Q..."
    "player_kill_code" : 1234
}
```

### Request Target

This endpoint will return the name of the target of the player who navigated here.

#### HTTP Request
---
```
GET http://<localhost>/player_access/request_target
	headers: Authorization: "Bearer dyJ0eXAiOiJKV1Q..."
```

#### URL Parameters
---

None

#### Return Value
---

```
{
    "target_first_name":"example"
    "target_last_name":"example"
}
```

### Remove From Game

Remove yourself from the game after you've died.

#### HTTP Request
---
```
GET http://<localhost>/player_access/remove_from_game
	headers: Authorization: "Bearer dyJ0eXAiOiJKV1Q..."
```

#### URL Parameters
---

None

#### Return Value
---


```
{
    "message" : "success"
}
```

### Quit Game

Allows a player to quit the game. This will remove the player, and if the game is started and this was the second to last player, will set the game state to 2 (meaning the game is won)

#### HTTP Request
---
```
GET http://<localhost>/player_access/quit_game
	headers: Authorization: "Bearer dyJ0eXAiOiJKV1Q..."
```

#### URL Parameters
---

None

#### Return Value
---

```
{
    "message" : "success"
}
```

## Game Creator Requests
### Create Game

This endpoint will create the game with the specified name and rules.

#### HTTP Request
---
```
POST http://<localhost>/creator_access/create_game
    {
        "game_name":"example"
        "game_rules":"example rules"
    }
```

#### URL Parameters
---
| Parameter | Default | Description
| ------ | ------ | ------|
| game_name | None | The name of the game |
| game_rules | None | The rules of the game |

#### Return Value
---

```
{
    "game_code": 9999
}
```

### Start Hunt
This endpoint will start hunting phase of the game of the game creator. This request can only be made by a game creator. Will return ```win: true``` if the game is won,  ```win: false``` otherwise.

#### HTTP Request
---
```
GET http://<localhost>/creator_access/start_hunt
 	headers: Authorization: "Bearer dyJ0eXAiOiJKV1Q..."
```

#### URL Parameters
---

None

##### Return Value
---
```
{
	"win": true
}
```

### Player List

This endpoint will return a list of the names of the players in the game.

#### HTTP Request
---
```
GET http://<localhost>/creator_access/player_list
	headers: Authorization: "Bearer dyJ0eXAiOiJKV1Q..."
```

#### URL Parameters
---

None

##### Return Value
---
```
{
  "players":
  [
      {
          "player_first_name": "test1"
          "player_last_name": "test1"
      },
      {
          "player_first_name": "test2"
          "player_last_name": "test2"
      }
  ]
}
```

## Status Requests

### Is Alive

This endpoint will tell the player asking if they are alive or not

#### HTTP Request
---
```
GET http://<localhost>/status_access/is_alive
	headers: Authorization: "Bearer dyJ0eXAiOiJKV1Q..."
```

#### URL Parameters
---

None

#### Return Value
---
```
{
    "is_alive": true
}
```

### Game State

This endpoint will return whether the specified game hasn't started (0) has started (1), or was won (2)

#### HTTP Request
---
```
POST http://<localhost>/status_access/game_state
    {
        "game_code": 9999
    }
```

#### URL Parameters
---
| Parameter | Default | Description
| ------ | ------ | ------|
| game_code | None | The 4 digit code of the game the player is in |

#### Return Value
---
```
{
    "game_state": 1
}
```

## Debug Requests
_Note: These requests should only be used for testing, and not used in the actual app_

### Get All Players

This endpoint will get all the information about the all the players on the server.

#### HTTP Request
---
```
GET http://<localhost>/test_access/get_all_players
```

#### URL Parameters
---
None
#### Return Value
---
A JSON list, where each entry contains the following:
```
{
    "player_id": 0
    "player_first_name": "example"
    "player_last_name": "example"
    "target_id": 0
    "target_first_name":"example"
    "target_last_name":"example"
    "is_alive": true
    "is_creator": false
    "game_code": 9999
}
```

### Get All Games

This endpoint will get all the information about all the games on the server.

#### HTTP Request
---
```
POST http://<localhost>/test_access/get_all_games
    {
        "game_code": 9999
    }
```

#### URL Parameters
---
None
#### Return Value
---
A JSON list, where each entry contains the following:
```
{
    "game_id": 0
    "game_name": "name"
    "game_rules": "rules"
    "game_code": 9999
    "game_state": 0
}
```


## Errors
The assassin-server API uses the following error codes:
  
| Error ID | Status Code | Description |
| -------- | ----------- | ----------- |
| 0 | 400 | "The game does not exist" |
| 1 | 400 | "The game is already started" |
| 2 | 400 | "The name you tried to join with is already taken" |
| 3 | 400 | "There is already a creator of this game" |
| 4 | 403 | "There is no player associated with this device" |
| 5 | 400 | "You don't have a target" |
| 6 | 403 | "You aren't the creator of  this game" |
| 7 | 400 | "You must supply a name for this game" |
| 8 | 500 | "There are no more available game codes" |
| 9 | 400 | "You are not dead or the last player" |
| 10 | 400 | "Incorrect killcode" |
| 11 | 400 | "The hunt hasn't started yet" |
| 12 | 422 | "This JWT token is invalid" |
| 13 | 401 | "Please supply a JWT token" |

The status codes correspond to:   

| Parameter | Default |
| ------ | ------ |
| 400 | Bad Request -- Your request was bad, maybe there is no such player or game, a player with that name already exists, etc. Check the server code to find out why. |
| 401 | JWT Issue --  Your JWT is expired or wasn't supplied |
| 403 | Forbidden -- You don't have the privileges to make that request |
| 422 | Malformed JWT -- Your JWT is broken somehow |
| 500 | Internal Server Error -- Something went wrong with the server! Oh no!!
