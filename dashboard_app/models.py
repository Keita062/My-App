from extensions import db
from datetime import datetime

class AnalysisHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    analysis_date = db.Column(db.DateTime, default=datetime.utcnow)
    result_summary = db.Column(db.Text)