from flask_survey_app.extensions import db
from datetime import datetime

class Company(db.Model):
    """
    企業研究情報を保存するためのモデル
    """
    __bind_key__ = 'research'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # A. 企業基本情報
    company_name = db.Column(db.String(200), nullable=False)
    industry = db.Column(db.String(100))
    website_url = db.Column(db.String(255))
    recruit_url = db.Column(db.String(255))
    business_content = db.Column(db.Text)
    philosophy = db.Column(db.Text)
    
    # B. 就活管理ステータス
    selection_status = db.Column(db.String(50), default='未応募')
    interest_level = db.Column(db.String(10), default='中')
    applied_position = db.Column(db.String(100))
    
    # C. 企業分析メモ
    strength_features = db.Column(db.Text)
    weakness_issues = db.Column(db.Text)
    culture = db.Column(db.Text)
    recent_news = db.Column(db.Text)
    free_memo = db.Column(db.Text)
    
    # D. 選考イベント記録
    event_memo = db.Column(db.Text)
    interview_memo = db.Column(db.Text)
    interview_date = db.Column(db.Date, nullable=True) # カレンダー連携用
    es_deadline = db.Column(db.Date, nullable=True) # カレンダー連携用

    # E. マイページ情報
    mypage_id = db.Column(db.String(100))
    mypage_password = db.Column(db.String(100))
    registration_date = db.Column(db.Date, default=datetime.utcnow)

    def __repr__(self):
        return f'<Company {self.company_name}>'
