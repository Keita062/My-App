from extensions import db
from datetime import datetime

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100), nullable=False)
    industry = db.Column(db.String(50))
    url = db.Column(db.String(200))
    memo = db.Column(db.Text)
    es_deadline = db.Column(db.Date, nullable=True)
    
    events = db.relationship('SelectionEvent', backref='company', lazy=True, cascade="all, delete-orphan")

class SelectionEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    event_type = db.Column(db.String(50), nullable=False) # 例: 説明会, ES, 1次面接
    event_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(50)) # 例: 予約済, 参加済, 結果待ち, 合格, 不合格
    notes = db.Column(db.Text)