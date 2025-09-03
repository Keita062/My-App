from extensions import db
from datetime import datetime

class Survey(db.Model):
    __bind_key__ = 'survey'
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100), nullable=False)
    course_name = db.Column(db.String(100), nullable=True)
    entry_date = db.Column(db.Date, nullable=False)
    deadline = db.Column(db.Date, nullable=False)
    questions = db.relationship('QuestionAnswer', backref='survey', cascade='all, delete-orphan')

class QuestionAnswer(db.Model):
    __bind_key__ = 'survey'
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=True)
    survey_id = db.Column(db.Integer, db.ForeignKey('survey.id'), nullable=False)

class Log(db.Model):
    __bind_key__ = 'logs'
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(100))
    path = db.Column(db.String(200))
    method = db.Column(db.String(10))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)