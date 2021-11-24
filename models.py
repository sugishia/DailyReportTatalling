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

    #活動参加者数
    in_party = db.Column(db.Integer, default=1)
    out_party = db.Column(db.Integer, default=0)
    
    #スタンディング実施数
    standing = db.Column(db.Integer, default=0)
    
    #全戸ビラ配布
    leaf_m = db.Column(db.Integer, default=0)
    leaf_a = db.Column(db.Integer, default=0)

    #対話・支持拡大
    dialogue = db.Column(db.Integer, default=0)
    support = db.Column(db.Integer, default=0)

    #働きかけ数
    workon_join = db.Column(db.Integer, default=0)
    join = db.Column(db.Integer, default=0)
    akahata_h = db.Column(db.Integer, default=0)
    akahata_n = db.Column(db.Integer, default=0)
    support_member = db.Column(db.Integer, default=0)
    ask_favor = db.Column(db.Integer, default=0)
    comment = db.Column(db.Text, nullable=True)

    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False)
    created_at = db.Column(db.DateTime)

    def __init__(self, date, in_party, out_party, standing, leaf_m, leaf_a, dialogue, support, 
    workon_join, join, akahata_h, akahata_n, support_member, ask_fover, comment, branch_id):
        self.date = date
        self.in_party = in_party
        self.out_party = out_party
        self.standing = standing
        self.leaf_m = leaf_m
        self.leaf_a = leaf_a
        self.dialogue = dialogue
        self.support = support
        self.workon_join = workon_join
        self.join = join
        self.akahata_h = akahata_h
        self.akahata_n = akahata_n
        self.support_member = support_member
        self.ask_favor = ask_fover
        self.comment = comment

        self.branch_id = branch_id
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

class Branch_Report_Status(db.Model):
    __tablename__ = 'branch_report_statuses'

    id = db.Column(db.Integer, primary_key=True)
    is_debate = db.Column(db.Boolean, default=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False)

    def __init__(self, is_debate, branch_id):
        self.is_debate = is_debate
        self.branch_id = branch_id

class Branch_Report_Totals(db.Model):
    __tablename__ = 'branch_report_totals'

    id = db.Column(db.Integer, primary_key=True)
    #活動参加者数
    in_party = db.Column(db.Integer, default=1)
    out_party = db.Column(db.Integer, default=0)
    
    #スタンディング実施数
    standing = db.Column(db.Integer, default=0)
    
    #全戸ビラ配布
    leaf_m = db.Column(db.Integer, default=0)
    leaf_a = db.Column(db.Integer, default=0)

    #対話・支持拡大
    dialogue = db.Column(db.Integer, default=0)
    support = db.Column(db.Integer, default=0)

    #働きかけ数
    workon_join = db.Column(db.Integer, default=0)
    join = db.Column(db.Integer, default=0)
    akahata_h = db.Column(db.Integer, default=0)
    akahata_n = db.Column(db.Integer, default=0)
    support_member = db.Column(db.Integer, default=0)
    ask_favor = db.Column(db.Integer, default=0)

    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False)

    def __init__(self, date, in_party, out_party, standing, leaf_m, leaf_a, dialogue, support, 
    workon_join, join, akahata_h, akahata_n, support_member, ask_fover,  branch_id):
        self.date = date
        self.in_party = in_party
        self.out_party = out_party
        self.standing = standing
        self.leaf_m = leaf_m
        self.leaf_a = leaf_a
        self.dialogue = dialogue
        self.support = support
        self.workon_join = workon_join
        self.join = join
        self.akahata_h = akahata_h
        self.akahata_n = akahata_n
        self.support_member = support_member
        self.ask_favor = ask_fover
        self.branch_id = branch_id