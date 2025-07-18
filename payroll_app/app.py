# payroll_app/app.py
from flask import Blueprint, render_template, request, redirect, url_for
from datetime import datetime
from sqlalchemy import func, extract
from flask_survey_app.extensions import db
from .models import WorkRecord

payroll_bp = Blueprint(
    'payroll', 
    __name__,
    template_folder='templates'
)

# --- 給与単価の定義 (変更なし) ---
PAY_RATES = {
    'REHATCH': {'hourly': 1170},
    '明光義塾': {
        '授業': {'value': 2333, 'minutes': 105},
        '事務': {'value': 1163, 'minutes': 60}
    }
}

def calculate_salary(record):
    delta = record.end_time - record.start_time
    duration_minutes = delta.total_seconds() / 60
    record.duration_minutes = int(duration_minutes)
    
    salary = 0
    if record.workplace == 'REHATCH':
        rate = PAY_RATES['REHATCH']['hourly']
        salary = (duration_minutes / 60) * rate
    elif record.workplace == '明光義塾':
        work_type_details = PAY_RATES['明光義塾'].get(record.work_type)
        if work_type_details:
            units = duration_minutes / work_type_details['minutes']
            salary = units * work_type_details['value']
            
    record.salary = int(round(salary))
    return record


@payroll_bp.route('/')
def dashboard():
    """ダッシュボードを表示"""
    current_year = datetime.now().year
    
    total_salary = db.session.query(func.sum(WorkRecord.salary)).filter(
        extract('year', WorkRecord.work_date) == current_year
    ).scalar() or 0

    monthly_summary = db.session.query(
        extract('month', WorkRecord.work_date).label('month'),
        WorkRecord.workplace,
        func.sum(WorkRecord.salary).label('total_salary')
    ).filter(
        extract('year', WorkRecord.work_date) == current_year
    ).group_by('month', WorkRecord.workplace).all()
    
    monthly_data = {}
    for month, workplace, salary in monthly_summary:
        if month not in monthly_data:
            monthly_data[month] = {'total': 0, '明光義塾': 0, 'REHATCH': 0}
        monthly_data[month][workplace] = salary
        monthly_data[month]['total'] += salary

    recent_records = WorkRecord.query.order_by(WorkRecord.start_time.desc()).limit(10).all()

    return render_template('payroll/dashboard.html',
                           total_salary=total_salary,
                           monthly_data=monthly_data,
                           recent_records=recent_records,
                           current_year=current_year) # 【追加】年をテンプレートに渡す

# 月間詳細ページ用のルート
@payroll_bp.route('/monthly/<int:year>/<int:month>')
def monthly_detail(year, month):
    """指定された月の詳細な勤務記録とサマリーを表示する"""
    
    # 指定された月の勤務記録を取得
    records = WorkRecord.query.filter(
        extract('year', WorkRecord.work_date) == year,
        extract('month', WorkRecord.work_date) == month
    ).order_by(WorkRecord.work_date.asc()).all()

    # 月間合計を計算
    total_salary = sum(r.salary for r in records)
    total_duration = sum(r.duration_minutes for r in records)

    # 勤務先ごとの合計を計算
    workplace_summary = {
        '明光義塾': {'salary': 0, 'duration': 0},
        'REHATCH': {'salary': 0, 'duration': 0}
    }
    for r in records:
        if r.workplace in workplace_summary:
            workplace_summary[r.workplace]['salary'] += r.salary
            workplace_summary[r.workplace]['duration'] += r.duration_minutes

    return render_template('payroll/monthly_detail.html',
                           year=year,
                           month=month,
                           records=records,
                           total_salary=total_salary,
                           total_duration=total_duration,
                           workplace_summary=workplace_summary)


# --- 勤務記録の追加・編集・削除  ---
@payroll_bp.route('/record/new', methods=['GET', 'POST'])
def new_record():
    if request.method == 'POST':
        start_datetime = datetime.strptime(f"{request.form['work_date']} {request.form['start_time']}", '%Y-%m-%d %H:%M')
        end_datetime = datetime.strptime(f"{request.form['work_date']} {request.form['end_time']}", '%Y-%m-%d %H:%M')
        
        new_rec = WorkRecord(
            work_date=datetime.strptime(request.form['work_date'], '%Y-%m-%d').date(),
            workplace=request.form['workplace'],
            work_type=request.form.get('work_type'),
            start_time=start_datetime,
            end_time=end_datetime
        )
        new_rec = calculate_salary(new_rec)
        db.session.add(new_rec)
        db.session.commit()
        return redirect(url_for('payroll.dashboard'))
    
    return render_template('payroll/record_form.html', record=None)

@payroll_bp.route('/record/edit/<int:id>', methods=['GET', 'POST'])
def edit_record(id):
    record = WorkRecord.query.get_or_404(id)
    if request.method == 'POST':
        start_datetime = datetime.strptime(f"{request.form['work_date']} {request.form['start_time']}", '%Y-%m-%d %H:%M')
        end_datetime = datetime.strptime(f"{request.form['work_date']} {request.form['end_time']}", '%Y-%m-%d %H:%M')
        
        record.work_date = datetime.strptime(request.form['work_date'], '%Y-%m-%d').date()
        record.workplace = request.form['workplace']
        record.work_type = request.form.get('work_type')
        record.start_time = start_datetime
        record.end_time = end_datetime

        record = calculate_salary(record)
        db.session.commit()
        return redirect(url_for('payroll.dashboard'))
        
    return render_template('payroll/record_form.html', record=record)

@payroll_bp.route('/record/delete/<int:id>', methods=['POST'])
def delete_record(id):
    record = WorkRecord.query.get_or_404(id)
    db.session.delete(record)
    db.session.commit()
    return redirect(url_for('payroll.dashboard'))
