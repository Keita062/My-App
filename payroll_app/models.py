# payroll_app/models.py
from flask_survey_app.extensions import db
from datetime import datetime

class WorkRecord(db.Model):
    """
    勤務記録を保存するためのモデル
    """
    __bind_key__ = 'payroll'
    
    id = db.Column(db.Integer, primary_key=True)
    work_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    workplace = db.Column(db.String(50), nullable=False) # 明光義塾 or REHATCH
    work_type = db.Column(db.String(50)) # 授業, 事務, or None
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    
    # 計算結果を保存
    duration_minutes = db.Column(db.Integer)
    salary = db.Column(db.Integer)

    def __repr__(self):
        return f'<WorkRecord {self.workplace} on {self.work_date}>'
