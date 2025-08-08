from extensions import db
from datetime import datetime

class Idea(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    creation_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    category = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    due_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f'<Idea {self.title}>'