# work_report_app/models.py
from flask_survey_app.extensions import db
from datetime import datetime

class Report(db.Model):
    """
    日報データを保存するためのモデル
    """
    __bind_key__ = 'report'
    
    id = db.Column(db.Integer, primary_key=True)
    report_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    
    # 開始報告
    scheduled_start_time = db.Column(db.String(50))
    scheduled_end_time = db.Column(db.String(50))
    scheduled_tasks = db.Column(db.Text)
    goals = db.Column(db.Text)
    
    # 完了報告
    actual_start_time = db.Column(db.String(50))
    actual_end_time = db.Column(db.String(50))
    completed_tasks = db.Column(db.Text)
    reflection = db.Column(db.Text)

    # 0: 開始報告のみ, 1: 完了報告済み
    status = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<Report {self.report_date.strftime("%Y-%m-%d")}>'
