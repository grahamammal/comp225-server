import os
import redis

from flask import Flask, session, abort, render_template, jsonify
from flask_session import Session
from datetime import timedelta

SESSION_TYPE = 'redis'
PERMANANT_SESSION_LIFETIME = timedelta(days=365)
sess = Session()

def create_app(test_config=None):
    """Creates app with specified config"""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=b'_5#y2L"F4Q8z\n\xec]/',
        DATABASE=os.path.join(app.instance_path, 'assassin_server.sqlite'),
        SESSION_TYPE='filesystem'
    )



    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)


    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    #intialises session on server
    sess.init_app(app)

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'


    #adds database to the app
    from . import db
    db.init_app(app)

    #adds the player_access blueprint to the app
    from . import player_access
    app.register_blueprint(player_access.bp)

    #adds the test_access blueprint to the app
    from . import debug_access
    app.register_blueprint(debug_access.bp)

    #adds the creator_access blueprint to the app
    from . import creator_access
    app.register_blueprint(creator_access.bp)

    #adds the status_access blueprint to the app
    from . import status_access
    app.register_blueprint(status_access.bp)


    return app

def internal_error(error_id):
    error_dict={
        0: jsonify({'message':'The game does not exist', 'error_id':0}),
        1: jsonify({'message':'The game is already started', 'error_id':1}),
        2: jsonify({'message':'The name you tried to join with is already taken', 'error_id':2}),
        3: jsonify({'message':'There is already a creator of this game', 'error_id':3}),
        4: jsonify({'message':'There is no player associated with this device', 'error_id':4}),
        5: jsonify({'message':'You do not have a target', 'error_id':5}),
        6: jsonify({'message':'You are not the creator of this game', 'error_id':6}),
        7: jsonify({'message':'You must supply a name for this game', 'error_id':7}),
        8: jsonify({'message':'There are no more available game codes', 'error_id':8}),
        9: jsonify({'message':'You are not dead or the last player', 'error_id':9}),
        10: jsonify({'message':'Incorrect killcode', 'error_id':10})
    }

    return error_dict[error_id]
