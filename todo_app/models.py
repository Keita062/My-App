from extensions import db  # 共通のextensions.pyからdbをインポート
from datetime import datetime

class Todo(db.Model):
    # __bind_key__ はconfigで設定するので、モデルからは削除します
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<Task {self.id}>'