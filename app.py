from flask import Flask
from flask.ext.login import LoginManager
from flask.ext.sqlalchemy import SQLAlchemy
import soundcloud
# Flask App Stuff
app = Flask(__name__)
app.secret_key = 'a'
app.debug = True

# DB Stuff
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root@localhost/mixt'
db = SQLAlchemy(app)
db.init_app(app)

# Login Stuff
login_manager = LoginManager()
login_manager.init_app(app)

# Soundcloud Stuff
cid = "2ef911abd6ebf9552964b6816f5b7d5b"
client = soundcloud.Client(client_id=cid)
