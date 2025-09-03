from flask import Blueprint, render_template, request, redirect, url_for, flash
from .models import db, Employee, Payroll, HistoricalPayroll
from datetime import datetime
from sqlalchemy import func

payroll_bp = Blueprint('payroll', __name__, template_folder='templates')

# ★★★★★ここが修正点です★★★★★
@payroll_bp.route('/') # '/dashboard' を '/' に変更
def dashboard():
    employees = Employee.query.all()
    payrolls = Payroll.query.all()
    historical_payrolls = HistoricalPayroll.query.all()
    
    # payrollsリストからtotal_salaryの合計を計算
    total_salary = sum(p.total_salary for p in payrolls if p.total_salary is not None)
    
    # 計算したtotal_salaryをテンプレートに渡す
    return render_template(
        'payroll/dashboard.html', 
        employees=employees, 
        payrolls=payrolls, 
        historical_payrolls=historical_payrolls, 
        total_salary=total_salary
    )

@payroll_bp.route('/employee/<int:employee_id>')
def employee_detail(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    return render_template('payroll/employee_detail.html', employee=employee)

@payroll_bp.route('/record/<int:record_id>')
def record_detail(record_id):
    record = Payroll.query.get_or_404(record_id)
    return render_template('payroll/record_detail.html', record=record)

@payroll_bp.route('/record/new', methods=['GET', 'POST'])
def new_record():
    if request.method == 'POST':
        # フォーム処理
        pass
    return render_template('payroll/record_form.html')