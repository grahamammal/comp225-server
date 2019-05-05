from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Players(db.Model):
    __tablename__ = 'players'

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
        return {c.name: getattr(self, c.name) for c in self.__table__.columns} # from : https://stackoverflow.com/questions/5022066/how-to-serialize-sqlalchemy-result-to-json

class Games(db.Model):
    __tablename__ = 'games'
    game_id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    game_name = db.Column(db.String(100), nullable = False)
    game_rules = db.Column(db.String(100))
    game_code = db.Column(db.Integer, unique = True, nullable = False)

    game_state = db.Column(db.Integer, nullable = False)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

def table_to_dict(table):
    output = []
    for row in table:
        output.append(row.as_dict())
