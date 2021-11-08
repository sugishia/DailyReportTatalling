from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import UserMixin
from flask_bcrypt import check_password_hash, generate_password_hash
from sqlalchemy.orm import backref, create_session
from app import app

import pytz

db = SQLAlchemy(app)
Migrate(app, db)

class DailyReport(db.Model):

    __tablename__ = 'dairy_reports'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    in_party = db.Column(db.Integer, default=1)
    out_party = db.Column(db.Integer, default=0)
    readed = db.Column(db.Integer, default=0)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False)
    is_debate = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime)

    def __init__(self, date, in_party, out_party, readed, branch_id, is_debate):
        self.date = date
        self.in_party = in_party
        self.out_party = out_party
        self.readed = readed
        self.branch_id = branch_id
        self.is_debate = is_debate
        self.created_at = datetime.now(pytz.timezone('Asia/Tokyo'))


class Branch(db.Model, UserMixin):
    __tablename__ = 'branches'

    id = db.Column(db.Integer, primary_key=True)
    branch_name = db.Column(db.String(30), unique=True, nullable=False)
    login_name = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(30), nullable=False)
    is_commissioner = db.Column(db.Boolean, nullable=False)
    created_at = db.Column(db.DateTime)

    report = db.relationship('DailyReport', backref='dairy_reports')

    def __init__(self, branch_name, login_name, password, is_commissioner):
        self.branch_name = branch_name
        self.login_name = login_name
        self.password = password
        self.is_commissioner = is_commissioner
        self.created_at = datetime.now(pytz.timezone('Asia/Tokyo'))