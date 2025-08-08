from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import db
from .models import Employee, Payroll, HistoricalPayroll

payroll_bp = Blueprint('payroll', __name__, template_folder='templates')

@payroll_bp.route('/')
def dashboard():
    employees = Employee.query.all()
    # 最新の給与データのみを取得するなどのロジックを追加するとより良くなります
    payrolls = Payroll.query.order_by(Payroll.year.desc(), Payroll.month.desc()).all()
    historical_payrolls = HistoricalPayroll.query.order_by(HistoricalPayroll.year.desc(), HistoricalPayroll.month.desc()).all()
    return render_template('payroll/dashboard.html', employees=employees, payrolls=payrolls, historical_payrolls=historical_payrolls)

@payroll_bp.route('/record', methods=['GET', 'POST'])
def record_form():
    if request.method == 'POST':
        try:
            employee_id = int(request.form.get('employee_id'))
            year = int(request.form.get('year'))
            month = int(request.form.get('month'))
            overtime_hours = float(request.form.get('overtime_hours', 0))
            deductions = int(request.form.get('deductions', 0))

            # 既存のデータがないか確認
            existing_payroll = Payroll.query.filter_by(employee_id=employee_id, year=year, month=month).first()
            if existing_payroll:
                flash(f'{year}年{month}月のデータは既に存在します。', 'error')
            else:
                new_payroll = Payroll(
                    employee_id=employee_id,
                    year=year,
                    month=month,
                    overtime_hours=overtime_hours,
                    deductions=deductions
                )
                db.session.add(new_payroll)
                db.session.commit()
                flash('給与データを登録しました。', 'success')
            return redirect(url_for('payroll.dashboard'))
        except (ValueError, TypeError) as e:
            flash(f'入力値が無効です: {e}', 'error')
            
    employees = Employee.query.all()
    return render_template('payroll/record_form.html', employees=employees)

@payroll_bp.route('/historical_record', methods=['GET', 'POST'])
def historical_record_form():
    if request.method == 'POST':
        try:
            new_record = HistoricalPayroll(
                year=int(request.form['year']),
                month=int(request.form['month']),
                total_payment=int(request.form['total_payment']),
                health_insurance=int(request.form['health_insurance']),
                pension=int(request.form['pension']),
                unemployment_insurance=int(request.form['unemployment_insurance']),
                income_tax=int(request.form['income_tax']),
                resident_tax=int(request.form['resident_tax'])
            )
            db.session.add(new_record)
            db.session.commit()
            flash('過去の給与データを登録しました。', 'success')
            return redirect(url_for('payroll.dashboard'))
        except (ValueError, TypeError) as e:
            flash(f'入力値が無効です: {e}', 'error')

    return render_template('payroll/historical_record_form.html')

@payroll_bp.route('/detail/<int:year>/<int:month>')
def monthly_detail(year, month):
    records = HistoricalPayroll.query.filter_by(year=year, month=month).all()
    return render_template('payroll/monthly_detail.html', records=records, year=year, month=month)