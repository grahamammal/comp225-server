import os
import redis

from flask import Flask, session, abort, render_template
from flask_session import Session


SESSION_TYPE = 'redis'
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
        abort(400)
        return "Hello"

    @app.errorhandler(400)
    def bad_request(error):
        return render_template('bad_request.html'), 400

    @app.errorhandler(403)
    def forbidden(error):
        return render_template('forbidden.html'), 403



    #adds database to the app
    from . import db
    db.init_app(app)

    #adds the player_access blueprint to the app
    from . import player_access
    app.register_blueprint(player_access.bp)

    #adds the test_access blueprint to the app
    from . import test_access
    app.register_blueprint(test_access.bp)

    #adds the creator_access blueprint to the app
    from . import creator_access
    app.register_blueprint(creator_access.bp)

    app.register_error_handler(400, bad_request)
    app.register_error_handler(403, forbidden)

    return app
