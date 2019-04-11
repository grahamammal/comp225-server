
# Assassin Server API Docs
_Analeidi Barrera,_
_Ellen Graham,_
_Corey Pieper,_
_Jacob Weightman_

# Table Of Contents
- [Player Requests](#player-requests)
  * [Get Game Info](#get-game-info)
    + [HTTP Request](#http-request)
    + [URL Parameters](#url-parameters)
    + [Return Value](#return-value)
  * [Got Target](#got-target)
    + [HTTP Request](#http-request-1)
    + [URL Parameters](#url-parameters-1)
    + [Return Value](#return-value-1)
  * [Won Game](#won-game)
    + [HTTP Request](#http-request-2)
    + [URL Parameters](#url-parameters-2)
    + [Return Value](#return-value-2)
  * [Add Player](#add-player)
    + [HTTP Request](#http-request-3)
    + [URL Parameters](#url-parameters-3)
    + [Return Value](#return-value-3)
  * [Request Target](#request-target)
    + [HTTP Request](#http-request-4)
    + [URL Parameters](#url-parameters-4)
    + [Return Value](#return-value-4)
- [Game Creator Requests](#game-creator-requests)
  * [Create Game](#create-game)
    + [HTTP Request](#http-request-5)
    + [URL Parameters](#url-parameters-5)
    + [Return Value](#return-value-5)
  * [Start Hunt](#start-hunt)
    + [HTTP Request](#http-request-6)
    + [URL Parameters](#url-parameters-6)
      - [Return Value](#return-value-6)
- [Status Requests](#status-requests)
  * [Is Alive](#is-alive)
    + [HTTP Request](#http-request-7)
    + [URL Parameters](#url-parameters-7)
    + [Return Value](#return-value-7)
  * [Is Game Started](#is-game-started)
    + [HTTP Request](#http-request-8)
    + [URL Parameters](#url-parameters-8)
    + [Return Value](#return-value-8)
- [Debug Requests](#debug-requests)
  * [Get Player](#get-player)
    + [HTTP Request](#http-request-9)
    + [URL Parameters](#url-parameters-9)
    + [Return Value](#return-value-9)
  * [Get All Players](#get-all-players)
    + [HTTP Request](#http-request-10)
    + [URL Parameters](#url-parameters-10)
    + [Return Value](#return-value-10)
  * [Get Game](#get-game)
    + [HTTP Request](#http-request-11)
    + [URL Parameters](#url-parameters-11)
    + [Return Value](#return-value-11)
  * [Get All Games](#get-all-games)
    + [HTTP Request](#http-request-12)
    + [URL Parameters](#url-parameters-12)
    + [Return Value](#return-value-12)
- [Errors](#errors)







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

This endpoint remove your target from the game and provide you with a new one. If you got the last other person, it will redirect to /won_game

#### HTTP Request
---
```
GET http://<localhost>/player_access/got_target
```

#### URL Parameters
---
None
#### Return Value
Status Code 302 if you won the game.

### Won Game

This endpoint tells you you won the game!

#### HTTP Request
---
```
GET http://<localhost>/player_access/won_game
```

#### URL Parameters
---
None

#### Return Value
---
```
{
	"won_game": true
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
        "is_creator": 0
        "game_code": 9999
    }
```

#### URL Parameters
---
| Parameter | Default | Description
| ------ | ------ | ------|
| player\_first\_name | None | The first name of the player |
| player\_last\_name | None | The last name of the player |
| is_creator | None | 1 if the player created the game, 0 otherwise |
| game_code | None | The 4 digit code of the game the player is joining |

#### Return Value
---
None

### Request Target

This endpoint will request the target of the player who navigated here.

#### HTTP Request
---
```
GET http://<localhost>/player_access/request_target
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
    "target_id": 0
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
|  | None | The name of the game |
| game_rules | None | The rules of the game |

#### Return Value
---

```
{
    "game_code": 9999
}
```

### Start Hunt

This endpoint will start hunting phase of the game of the game creator. This request can only be made by a game creator.

#### HTTP Request
---
```
GET http://<localhost>/creator_access/start_hunt
```

#### URL Parameters
---
None
##### Return Value
---
None

## Status Requests

### Is Alive

This endpoint will tell the player asking if they are alive or not

#### HTTP Request
---
```
GET http://<localhost>/status_access/is_alive
```

#### URL Parameters
---
None

#### Return Value
---
```
{
    "is_alive": 1
}
```

### Is Game Started

This endpoint will return whether the specified game has started or not

#### HTTP Request
---
```
POST http://<localhost>/status_access/is_game_started
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
    "is_alive": 1
}
```

## Debug Requests
_Note: These requests should only be used for testing, and not used in the actual app_
### Get Player

This endpoint will get all the information about the specified player.

#### HTTP Request
---
```
POST http://<localhost>/test_access/get_player
    {
        "player_first_name": "example"
        "player_last_name": "example"
        "game_code": 9999
    }
```

#### URL Parameters
---
| Parameter | Default | Description
| ------ | ------ | ------|
| player\_first\_name | None | The first name of the player |
| player\_last\_name | None | The last name of the player |
| game_code | None | The 4 digit code of the game the player is in |

#### Return Value
---
```
{
    "player_id": 0
    "player_first_name": "example"
    "player_last_name": "example"
    "target_id": 0
    "target_first_name":"example"
    "target_last_name":"example"
    "is_alive": 1
    "is_creator": 0
    "disputed_got": 0
    "game_code": 9999
}
```

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
    "is_alive": 1
    "is_creator": 0
    "disputed_got": 0
    "game_code": 9999
}
```

### Get Game

This endpoint will get all the information about the specified game.

#### HTTP Request
---
```
POST http://<localhost>/test_access/get_game
    {
        "game_code": 9999
    }
```

#### URL Parameters
---
| Parameter | Default | Description
| ------ | ------ | ------|
| game_code | None | The 4 digit code of the game you want the info of|

#### Return Value
---
```
{
    "game_id": 0
    "game_name": "name"
    "game_rules": "rules"
    "game_code": 9999
    "game_state": 0
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

| Parameter | Default |
| ------ | ------ |
| 400 | Bad Request -- Your request was bad, maybe there is no such player or game, a player with that name already exists, etc. Check the server code to find out why. |
| 403 | Forbidden -- You don't have the privileges to make that request |
| 500 | Internal Server Error -- Something went wrong with the server! Oh no!!
