from flask_sqlalchemy import SQLAlchemy
from assassin_server.__init__ import db

class Players(db.Model):
    player_id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    player_kill_code = db.Column(db.Integer)
    player_first_name = db.Column(db.String(50), nullable = False)
    player_last_name = db.Column(db.String(50), nullable = False)

    target_id = db.Column(db.Integer)
    target_first_name = db.Column(db.String(50))
    target_last_name = db.Column(db.String(50))

    is_alive = db.Column(db.Boolean, nullable = False)
    is_creator = db.Column(db.Boolean, nullable = False)

    game_code = db.Column(db.Integer, nullable = False)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Games(db.Model):
    game_id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    game_name = db.Column(db.String(100), nullable = False)
    game_code = db.Column(db.Integer, unique = True, nullable = False)

    game_state = db.Column(db.Integer, nullable = False)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
