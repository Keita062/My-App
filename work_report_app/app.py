from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime
from flask_survey_app.extensions import db
from .models import Report

report_bp = Blueprint(
    'report', 
    __name__,
    template_folder='templates',
    static_folder='static'
)

@report_bp.route('/')
def list_reports():
    """日報の一覧を表示"""
    all_reports = Report.query.order_by(Report.report_date.desc()).all()
    return render_template('report/list.html', reports=all_reports)

@report_bp.route('/new', methods=['GET', 'POST'])
def new_report():
    """新しい日報（開始報告）を作成"""
    if request.method == 'POST':
        new_report = Report(
            report_date=datetime.strptime(request.form['report_date'], '%Y-%m-%d').date(),
            scheduled_start_time=request.form['scheduled_start_time'],
            scheduled_end_time=request.form['scheduled_end_time'],
            scheduled_tasks=request.form['scheduled_tasks'],
            goals=request.form['goals'],
            status=0 # 開始報告のみ
        )
        db.session.add(new_report)
        db.session.commit()
        return redirect(url_for('report.list_reports'))
    
    today_str = datetime.today().strftime('%Y-%m-%d')
    return render_template('report/form.html', today=today_str, report=None)


@report_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_report(id):
    """日報の編集（完了報告）"""
    report = Report.query.get_or_404(id)
    if request.method == 'POST':
        # 完了報告の項目を更新
        report.actual_start_time = request.form['actual_start_time']
        report.actual_end_time = request.form['actual_end_time']
        report.completed_tasks = request.form['completed_tasks']
        report.reflection = request.form['reflection']
        report.status = 1 # 完了報告済みに更新
        db.session.commit()
        return redirect(url_for('report.list_reports'))
    
    return render_template('report/form.html', report=report)

@report_bp.route('/<int:id>')
def detail_report(id):
    """日報の詳細を表示"""
    report = Report.query.get_or_404(id)
    return render_template('report/detail.html', report=report)

@report_bp.route('/delete/<int:id>', methods=['POST'])
def delete_report(id):
    """日報を削除"""
    report_to_delete = Report.query.get_or_404(id)
    db.session.delete(report_to_delete)
    db.session.commit()
    return redirect(url_for('report.list_reports'))