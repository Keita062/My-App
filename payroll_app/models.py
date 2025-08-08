from extensions import db
from datetime import datetime

class Employee(db.Model):
    """従業員情報を管理するモデル"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    base_salary = db.Column(db.Integer, nullable=False, default=0)
    transportation_allowance = db.Column(db.Integer, nullable=False, default=0)

    # 従業員が削除されたときに、関連する給与データも削除されるように設定
    payrolls = db.relationship('Payroll', backref='employee', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Employee {self.name}>'


class Payroll(db.Model):
    """月ごとの給与計算データを管理するモデル"""
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    overtime_hours = db.Column(db.Float, nullable=False, default=0)
    deductions = db.Column(db.Integer, nullable=False, default=0)

    def __repr__(self):
        return f'<Payroll for {self.employee_id} - {self.year}/{self.month}>'


class HistoricalPayroll(db.Model):
    """手入力用の過去の給与データを管理するモデル"""
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    total_payment = db.Column(db.Integer, nullable=False)
    health_insurance = db.Column(db.Integer, nullable=False)
    pension = db.Column(db.Integer, nullable=False)
    unemployment_insurance = db.Column(db.Integer, nullable=False)
    income_tax = db.Column(db.Integer, nullable=False)
    resident_tax = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<HistoricalPayroll {self.year}/{self.month}>'