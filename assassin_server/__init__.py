import os
import redis

from flask import Flask, session
from flask_session import Session

SESSION_TYPE = 'redis'
sess = Session()

def create_app(test_config=None):
    # create and configure the app
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



    sess.init_app(app)

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'


    from . import db
    db.init_app(app)

    from . import player_access
    app.register_blueprint(player_access.bp)

    return app
