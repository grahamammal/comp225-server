# COMP225 Assassin Server
__A project by:__
* _Analeidi Barrera_
* _Ellen Graham_
* _Corey Pieper_
* _Jacob Weightman_
---
__Table of Contents__

- [Description](#Description)  
- [Local Setup](#Local-Setup)   
- [Testing](#Testing)   
- [Heroku Setup](#Heroku-Setup)

## Description
A server for the Assassin project by group Elcoanja. It acts as an API for the client side that stores the game state and player information. Documentation of the API can be found [here](https://github.com/grahamammal/comp225-server/blob/master/Assassin%20Server%20API.md). The client side can be accessed from [here](https://github.com/jacobdweightman/comp225-assassin). Planning information for the project can be found [here](https://www.notion.so/79e84c0ad6994fd7b4cd72364003f146?v=f6c490dd4698449b9141b8a116738678). You may need an account with privileges to access it. The server is built using flask with a postgreSQL database, and is hosted on [Heroku](https://elcoanja.herokuapp.com/). The initial code relied heavily on the tutorial from [Flask](http://flask.pocoo.org/docs/1.0/tutorial/).

## Getting Started Locally
To run the server locally, you'll first need to setup a virtual environment for the app. In your console:

On Mac:
```
python3 -m venv venv
```

On Windows:
```
py -3 -m venv venv
```


Then activate the virtual environment:

On Mac:
```
. venv/bin/activate
```

On Windows:
```
venv\Scripts\activate
```

Then install the dependencies:
```
pip install -r requirements.txt
```

Before running the app, you'll need to setup a postgreSQL database. First, install postgreSQL on your machine. Then create a database for the server to connect to. Once this is done, change the constant connecting to the database to your database URI. In `assassin_server\__init__.py`:    
```
app.config['SQLALCHEMY_DATABASE_URI'] = <your postgreSQL link>
```

In order to create the tables in the database, first open the python interpreter in the directory:

On Mac:
```
python3
```

On Windows:
```
venv\Scripts\python
```

Then run the following code:

```
from assassin_server.__init__ import create_app
from assassin_server.db_models import db
app = create_app()
app.app_context().push()

db.drop_all()
db.create_all()
```

Now the database should be ready. To run the app, return to the directory while in the virtual environment. Then run it:

On Mac:
```
export FLASK_APP=assassin_server
export FLASK_ENV=development
flask run
```

On Windows:
```
set FLASK_APP=assassin_server
set FLASK_ENV=development
flask run
```

## Testing
If you want to run the test suite instead:

On Mac:
```
export TEST_DATABASE_URL=<postgreSQL test link>
pytest
```

On Windows:
```
set TEST_DATABASE_URL=<ppostgreSQL test link>
pytest
```
Note that the database specified by the test link doesn't need to exist, as it will be created then torn down after tests run.

If you want to see the coverage of the unit tests, instead of `pytest` run:
```
coverage run -m pytest
coverage report
```
To see an html document of where the tests missed, run
```
coverage html
```
Then open `index.html` in `\htmlcov` with your browser.

## Getting Started on Heroku
To setup the server on Heroku, first deploy the current build from [the dashboard](https://dashboard.heroku.com/apps/elcoanja/deploy/github). Then, to setup the database, with the Heroku CLI installed run:

```
heroku run python start_db.py shell --app elcoanja
```

Note that you'll need to be signed in with an account with proper permissions in order to deploy to Heroku.
