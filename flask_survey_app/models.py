from extensions import db
from datetime import datetime

class Survey(db.Model):
    __bind_key__ = 'survey'
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100), nullable=False)
    deadline = db.Column(db.DateTime, nullable=True)
    questions = db.Column(db.Text)
    answers = db.Column(db.Text)
    status = db.Column(db.String(50))
    evaluation = db.Column(db.String(50))
    memo = db.Column(db.Text)

class Log(db.Model):
    __bind_key__ = 'logs'
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(100))
    path = db.Column(db.String(200))
    method = db.Column(db.String(10))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)