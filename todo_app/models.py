from flask_survey_app.extensions import db
from datetime import datetime

class Todo(db.Model):
    """
    ToDoタスクを保存するためのモデル
    """
    __bind_key__ = 'todo'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    due_date = db.Column(db.DateTime, nullable=True)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Todo {self.id}>'