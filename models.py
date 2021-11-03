from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app import app

db = SQLAlchemy(app)
Migrate(app, db)

class DailyReport(db.Model):

    __tablename__ = 'dairy_report'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    in_party = db.Column(db.Integer, default=1)
    out_party = db.Column(db.Integer, default=0)
    readed = db.Column(db.Integer, default=0)
    is_debate = db.Column(db.Boolean, default=False)

    def __init__(self, date, in_party, out_party, readed, is_debate):
        self.date = date
        self.in_party = in_party
        self.out_party = out_party
        self.readed = readed
        self.is_debate = is_debate