from flask import Flask
from flask_login import LoginManager
import os

app = Flask(__name__)

login_manager = LoginManager()
login_manager.init_app(app)

base_dir = os.path.dirname(__file__) #ファイルのパス

app.config['SECRET_KEY'] = os.urandom(16)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(base_dir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True


