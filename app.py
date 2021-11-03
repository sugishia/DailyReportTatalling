from flask import Flask
import os

app = Flask(__name__)

base_dir = os.path.dirname(__file__) #ファイルのパス

app.config['SECRET_KEY'] = os.urandom(16)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(base_dir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True


