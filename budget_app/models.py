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

class BudgetSimulation(db.Model):
    """
    作成した予算シミュレーションを保存するモデル
    """
    __bind_key__ = 'budget'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    simulation_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    # 基本設定の入力値を保存
    target_year = db.Column(db.Integer, nullable=False)
    target_month = db.Column(db.Integer, nullable=False)
    gross_amount = db.Column(db.Float, nullable=False)
    calculation_method = db.Column(db.String(10), nullable=False) # '内掛け' or '外掛け'
    commission_rate_used = db.Column(db.Float, nullable=False) # 使用した手数料率
    broadcast_amount = db.Column(db.Float, nullable=False, default=0)
    remaining_days = db.Column(db.Integer, nullable=False)
    
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    
    # クリエイティブごとの詳細な入力値と計算結果はJSON形式で保存
    simulation_details = db.Column(db.Text, nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    client = db.relationship('Client', backref='simulations')

    def __repr__(self):
        return f'<BudgetSimulation {self.title}>'