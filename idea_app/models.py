from flask_survey_app.extensions import db
from datetime import datetime

class Idea(db.Model):
    """
    アイディアを保存するためのモデル
    """
    __bind_key__ = 'idea'
    
    id = db.Column(db.Integer, primary_key=True)
    creation_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    title = db.Column(db.String(200), nullable=False)
    details = db.Column(db.Text)
    status = db.Column(db.String(50), nullable=False, default='未着手')
    category = db.Column(db.String(100))
    priority = db.Column(db.String(10), default='中')
    due_date = db.Column(db.Date)

    def __repr__(self):
        return f'<Idea {self.title}>'
