from assassin_server.__init__ import create_app
from assassin_server.db_models import db
app = create_app()
app.app_context().push()

db.drop_all()
db.create_all()
