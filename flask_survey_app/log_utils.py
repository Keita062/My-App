from .extensions import db
from datetime import datetime

class Log(db.Model):
    """
    アクセスログを保存するためのモデル
    """
    # このモデルが'logs'という名前のデータベースに紐づくことを指定
    __bind_key__ = 'logs'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    ip_address = db.Column(db.String(45), nullable=False)
    path = db.Column(db.String(200), nullable=False)
    method = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return f'<Log {self.timestamp} {self.ip_address} {self.path}>'