from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime
import json
from flask_survey_app.extensions import db
from .models import Report

report_bp = Blueprint(
    'report', 
    __name__,
    template_folder='templates',
    static_folder='static'
)

def parse_tasks_from_form(form):
    """フォームからタスクのリストを解析して返す"""
    descriptions = form.getlist('task_descriptions[]')
    durations = form.getlist('task_durations[]')
    return [{'desc': desc, 'duration': dur} for desc, dur in zip(descriptions, durations) if desc.strip()]

@report_bp.route('/')
def list_reports():
    """日報の一覧を表示"""
    all_reports = Report.query.order_by(Report.report_date.desc()).all()
    for report in all_reports:
        try:
            report.start_tasks = json.loads(report.start_scheduled_tasks) if report.start_scheduled_tasks else []
            report.end_tasks = json.loads(report.end_completed_tasks) if report.end_completed_tasks else []
        except (json.JSONDecodeError, TypeError):
            report.start_tasks = [{'desc': 'データ形式エラー', 'duration': ''}]
            report.end_tasks = [{'desc': 'データ形式エラー', 'duration': ''}]
    return render_template('report/list.html', reports=all_reports)

@report_bp.route('/new', methods=['GET', 'POST'])
def new_report():
    """新しい日報（開始報告）を作成"""
    if request.method == 'POST':
        report_date = datetime.strptime(request.form['report_date'], '%Y-%m-%d').date()
        if Report.query.filter_by(report_date=report_date).first():
            flash(f'{report_date.strftime("%Y-%m-%d")}の報告は既に存在します。編集してください。', 'error')
            return redirect(url_for('report.list_reports'))

        start_tasks = parse_tasks_from_form(request.form)
        
        new_report = Report(
            report_date=report_date,
            start_scheduled_time=f"{request.form['start_time']} - {request.form['end_time']}",
            start_scheduled_tasks=json.dumps(start_tasks, ensure_ascii=False),
            start_goals=request.form['goals']
        )
        db.session.add(new_report)
        db.session.commit()
        flash('開始報告を登録しました。', 'success')
        return redirect(url_for('report.list_reports'))
    
    return render_template('report/form.html', form_type='new', report=None)

@report_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_report(id):
    """日報の編集（開始・完了報告の両方）"""
    report = Report.query.get_or_404(id)
    
    try:
        start_tasks = json.loads(report.start_scheduled_tasks) if report.start_scheduled_tasks else []
        end_tasks = json.loads(report.end_completed_tasks) if report.end_completed_tasks else []
    except (json.JSONDecodeError, TypeError):
        start_tasks, end_tasks = [], []

    if request.method == 'POST':
        # 開始報告の更新
        report.start_scheduled_time = f"{request.form['start_time']} - {request.form['end_time']}"
        start_tasks_list = [{'desc': d, 'duration': u} for d, u in zip(request.form.getlist('start_task_descriptions[]'), request.form.getlist('start_task_durations[]')) if d]
        report.start_scheduled_tasks = json.dumps(start_tasks_list, ensure_ascii=False)
        report.start_goals = request.form['goals']

        # 完了報告の更新 (入力があれば)
        if request.form.get('end_start_time'):
            report.end_actual_time = f"{request.form['end_start_time']} - {request.form['end_end_time']}"
            end_tasks_list = [{'desc': d, 'duration': u} for d, u in zip(request.form.getlist('end_task_descriptions[]'), request.form.getlist('end_task_durations[]')) if d]
            report.end_completed_tasks = json.dumps(end_tasks_list, ensure_ascii=False)
            report.end_reflection = request.form['reflection']
        
        db.session.commit()
        flash('日報を更新しました。', 'success')
        return redirect(url_for('report.list_reports'))

    return render_template('report/form.html', form_type='edit', report=report, start_tasks=start_tasks, end_tasks=end_tasks)

@report_bp.route('/delete/<int:id>', methods=['POST'])
def delete_report(id):
    report_to_delete = Report.query.get_or_404(id)
    db.session.delete(report_to_delete)
    db.session.commit()
    flash('日報を削除しました。', 'success')
    return redirect(url_for('report.list_reports'))