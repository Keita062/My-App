# payroll_app/app.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
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
    """勤務時間から給与を計算する関数"""
    if record.start_time and record.end_time:
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
    # (変更なし)
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
    ).group_by('month', 'workplace').all()
    
    monthly_data = {}
    for i in range(1, 13):
        monthly_data[i] = {'total': 0, '明光義塾': 0, 'REHATCH': 0}

    for month, workplace, salary in monthly_summary:
        if workplace in monthly_data[month]:
            monthly_data[month][workplace] = salary if salary else 0
        monthly_data[month]['total'] += salary if salary else 0

    recent_records = WorkRecord.query.order_by(WorkRecord.start_time.desc()).limit(10).all()

    return render_template('payroll/dashboard.html',
                           total_salary=total_salary,
                           monthly_data=monthly_data,
                           recent_records=recent_records,
                           current_year=current_year)


@payroll_bp.route('/monthly/<int:year>/<int:month>')
def monthly_detail(year, month):
    """指定された月の詳細な勤務記録とサマリーを表示する"""
    # (変更なし)
    records = WorkRecord.query.filter(
        extract('year', WorkRecord.work_date) == year,
        extract('month', WorkRecord.work_date) == month
    ).order_by(WorkRecord.work_date.asc()).all()

    total_salary = sum(r.salary for r in records if r.salary)
    total_duration = sum(r.duration_minutes for r in records if r.duration_minutes)

    workplace_summary = {
        '明光義塾': {'salary': 0, 'duration': 0},
        'REHATCH': {'salary': 0, 'duration': 0}
    }
    for r in records:
        if r.workplace in workplace_summary:
            workplace_summary[r.workplace]['salary'] += r.salary if r.salary else 0
            workplace_summary[r.workplace]['duration'] += r.duration_minutes if r.duration_minutes else 0

    return render_template('payroll/monthly_detail.html',
                           year=year,
                           month=month,
                           records=records,
                           total_salary=total_salary,
                           total_duration=total_duration,
                           workplace_summary=workplace_summary)


@payroll_bp.route('/record/new', methods=['GET', 'POST'])
def new_record():
    """通常の勤務記録を新規作成する"""
 
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
    
    return render_template('payroll/record_form.html', record=None, form_title="勤務記録の新規作成")

@payroll_bp.route('/record/add_historical', methods=['GET', 'POST'])
def add_historical_record():
    """手入力で過去の月次給与データを登録する"""
    if request.method == 'POST':
        try:
            year = int(request.form['year'])
            month = int(request.form['month'])
            salary = int(request.form['salary'])
            workplace = request.form['workplace']
            
            # 同じ年月、同じ勤務先のデータが既に存在するかチェック
            existing_record = WorkRecord.query.filter(
                extract('year', WorkRecord.work_date) == year,
                extract('month', WorkRecord.work_date) == month,
                WorkRecord.workplace == workplace,
                WorkRecord.work_type == '過去データ'
            ).first()

            if existing_record:
                flash(f'{year}年{month}月 ({workplace}) の過去データは既に登録されています。', 'error')
                return redirect(url_for('payroll.add_historical_record'))

            # 登録月の1日を日付として記録
            work_date = datetime(year, month, 1).date()
            
            new_rec = WorkRecord(
                work_date=work_date,
                workplace=workplace,
                work_type='過去データ', # 識別用
                start_time=None, # 時間は記録しない
                end_time=None,   # 時間は記録しない
                duration_minutes=0,
                salary=salary # 手入力された金額をそのまま保存
            )
            db.session.add(new_rec)
            db.session.commit()
            flash(f'{year}年{month}月 ({workplace}) の給与データを登録しました。', 'success')
            return redirect(url_for('payroll.dashboard'))

        except ValueError:
            flash('年度、月、金額には有効な数値を入力してください。', 'error')
        except Exception as e:
            flash(f'登録中にエラーが発生しました: {e}', 'error')
        
        return redirect(url_for('payroll.add_historical_record'))

    # GETリクエストの場合、登録フォームを表示
    return render_template('payroll/historical_record_form.html', form_title="過去の給与データを登録")


@payroll_bp.route('/record/edit/<int:id>', methods=['GET', 'POST'])
def edit_record(id):
    """勤務記録を編集する"""
    # (変更なし)
    record = WorkRecord.query.get_or_404(id)
    if request.method == 'POST':
        if record.work_type == '過去データ':
            flash('過去のデータは編集できません。削除してから再登録してください。', 'info')
            return redirect(url_for('payroll.dashboard'))

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
        
    return render_template('payroll/record_form.html', record=record, form_title="勤務記録の編集")

@payroll_bp.route('/record/delete/<int:id>', methods=['POST'])
def delete_record(id):
    """勤務記録を削除する"""
    # (変更なし)
    record = WorkRecord.query.get_or_404(id)
    db.session.delete(record)
    db.session.commit()
    flash('記録を削除しました。', 'success')
    return redirect(request.referrer or url_for('payroll.dashboard'))