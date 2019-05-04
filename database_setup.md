Go to a python shell

from assassin_server.\_\_init\_\_ import create_app
app = create_app()
app.app_context().push()

from assassin_server.__init__ import db

db.drop_all()
db.create_all()


__An example insertion and query__
me = db_models.Players(
    player_first_name = 'test',
    player_last_name = 'test',
    is_alive = 0,
    is_creator = 0,
    game_code = 1234
    )
db.session.add(me)
db.session.commit()

return jsonify(db_models.Players.query.filter_by(player_first_name='test').first().as_dict())
