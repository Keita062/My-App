from flask_survey_app.extensions import db
from datetime import datetime

class Memo(db.Model):
    """
    メモを保存するためのモデル
    """
    __bind_key__ = 'memo'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text)
    tags = db.Column(db.String(255)) # カンマ区切りの文字列でタグを保存
    is_pinned = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Memo {self.title}>'