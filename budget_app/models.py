from extensions import db

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(100), nullable=False, unique=True)
    base_fee = db.Column(db.Integer, nullable=False, default=0)

class BudgetSimulation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    month = db.Column(db.String(7), nullable=False) # YYYY-MM
    estimated_pv = db.Column(db.Integer)
    cvr = db.Column(db.Float)
    cpa = db.Column(db.Integer)
    
    client = db.relationship('Client', backref=db.backref('simulations', lazy=True))