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
export FLASK_APP=flaskr
export FLASK_ENV=development
flask init-db
flask run
```

On Windows:
```
set FLASK_APP=flaskr
set FLASK_ENV=development
flask init-db
flask run
```
