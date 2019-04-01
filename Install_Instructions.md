#Instructions for how to install and run the server

_Note: You will need python installed_

These instructions can be found at:  
http://flask.pocoo.org/docs/1.0/tutorial/


Go to the comp225-server directory in your terminal

Create a venv folder in the directory  
On Mac:
```
python3 -m venv venv
```
On Windows:
```
py -3 -m venv venv
```

Then activate the environment

On Mac:
```
. venv/bin/activate
```

On Windows
```
venv\Scripts\activate
```

Install flask

```
pip install Flask
```



Run the application:



On Mac:
```
export FLASK_APP=assassin_server
export FLASK_ENV=development
flask init-db
flask run
```

On Windows:
```
set FLASK_APP=assassin_server
set FLASK_ENV=development
flask init-db
flask run
```

Note: You only need to initialize the data base once, unless you want to reset it. However you need to set the app and env every time you start working on the app.
