from flask_survey_app.extensions import db
from datetime import datetime

class Client(db.Model):
    """
    クライアントと手数料率を管理するモデル
    """
    __bind_key__ = 'budget'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    # 手数料率はパーセントで保存 (例: 20% -> 20.0)
    commission_rate = db.Column(db.Float, nullable=False, default=20.0)

    def __repr__(self):
        return f'<Client {self.name}>'

class Budget(db.Model):
    """
    作成した予算シミュレーションを保存するモデル
    """
    __bind_key__ = 'budget'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    gross_amount = db.Column(db.Float, nullable=False)
    calculation_method = db.Column(db.String(10), nullable=False) # '内掛け' or '外掛け'
    broadcast_amount = db.Column(db.Float, nullable=False, default=0)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    
    # 計算結果やクリエイティブの内訳はJSON形式で保存
    simulation_data = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    client = db.relationship('Client', backref='budgets')

    def __repr__(self):
        return f'<Budget {self.title}>'