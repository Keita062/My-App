from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime
from flask_survey_app.extensions import db
from .models import Report

report_bp = Blueprint(
    'report', 
    __name__,
    template_folder='templates'
)

@report_bp.route('/')
def list_reports():
    """日報の一覧を表示"""
    all_reports = Report.query.order_by(Report.report_date.desc()).all()
    return render_template('report/list.html', reports=all_reports)

@report_bp.route('/select_type')
def select_type():
    reports_to_complete = Report.query.filter(Report.end_completed_tasks == None).order_by(Report.report_date.desc()).all()
    return render_template('report/select_type.html', reports_to_complete=reports_to_complete)

@report_bp.route('/new_start', methods=['GET', 'POST'])
def new_start_report():
    if request.method == 'POST':
        report_date_str = request.form['report_date']
        report_date = datetime.strptime(report_date_str, '%Y-%m-%d').date()

        existing_report = Report.query.filter_by(report_date=report_date).first()
        if existing_report:
            flash(f'{report_date_str}の開始報告は既に存在します。', 'error')
            return redirect(url_for('report.select_type'))

        new_report = Report(
            report_date=report_date,
            start_scheduled_time=f"{request.form['start_time']} - {request.form['end_time']}",
            start_scheduled_tasks=request.form['scheduled_tasks'],
            start_goals=request.form['goals']
        )
        db.session.add(new_report)
        db.session.commit()
        flash(f'{report_date_str}の開始報告を登録しました。', 'success')
        return redirect(url_for('report.list_reports'))
    
    return render_template('report/form.html', form_type='start', report=None)

@report_bp.route('/new_end/<int:id>', methods=['GET', 'POST'])
def new_end_report(id):
    report = Report.query.get_or_404(id)
    if request.method == 'POST':
        report.end_actual_time = f"{request.form['start_time']} - {request.form['end_time']}"
        report.end_completed_tasks = request.form['completed_tasks']
        report.end_reflection = request.form['reflection']
        db.session.commit()
        flash(f'{report.report_date.strftime("%Y-%m-%d")}の完了報告を登録しました。', 'success')
        return redirect(url_for('report.list_reports'))

    # form.htmlを「完了報告モード」で表示
    return render_template('report/form.html', form_type='end', report=report)

@report_bp.route('/delete/<int:id>', methods=['POST'])
def delete_report(id):
    report_to_delete = Report.query.get_or_404(id)
    db.session.delete(report_to_delete)
    db.session.commit()
    flash(f'{report_to_delete.report_date.strftime("%Y-%m-%d")}の日報を削除しました。', 'success')
    return redirect(url_for('report.list_reports'))