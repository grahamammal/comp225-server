# How to run the database on your local machine:

First install postgreSQL on your machine. I installed from https://www.enterprisedb.com/downloads/postgres-postgresql-downloads.
Supply a url to SQLALCHEMY_DATABASE_URI in ``` __init__.py```after you make a database

Go to a python shell

Run the following to create the tables
```
from assassin_server.__init__ import create_app
app = create_app()
app.app_context().push()

from assassin_server.db_models import db

db.drop_all()
db.create_all()
```
## An example insertion and query
me = db_models.Players(
    player_first_name = 'test',
    player_last_name = 'test',
    is_alive = 0,
    is_creator = 0,
    game_code = 1234
    )
db.session.add(me)
db.session.commit()
db_models.Players.query.filter_by(player_first_name='test').first()

## To run tests:
On Windows:
```
set TEST_DATABASE_URL=postgresql://postgres@localhost:5432/assassin_test_server
pytest
```
On Mac:
```
export TEST_DATABASE_URL=postgresql://postgres@localhost:5432/assassin_test_server
pytest
```
# To run on Heroku
First deploy to Heroku. Then in the command line run:
```
heroku run python start_db.py shell --app elcoanja
```
