from extensions import db  
from datetime import datetime

class Report(db.Model):
    """
    日報データを保存するためのモデル
    開始報告と完了報告を1つのレコードで管理
    """

    id = db.Column(db.Integer, primary_key=True)
    report_date = db.Column(db.Date, nullable=False, unique=True) # 日付はユニークに

    # --- 開始報告 ---
    start_scheduled_time = db.Column(db.String(50))
    start_scheduled_tasks = db.Column(db.Text)
    start_goals = db.Column(db.Text)
    
    # --- 完了報告 ---
    end_actual_time = db.Column(db.String(50), nullable=True)
    end_completed_tasks = db.Column(db.Text, nullable=True)
    end_reflection = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<Report {self.report_date}>'