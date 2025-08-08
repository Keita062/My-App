from flask import Blueprint, render_template, request, redirect, url_for, flash
from .models import Report
from extensions import db
from datetime import datetime

report_bp = Blueprint('work_report', __name__, template_folder='templates')

@report_bp.route('/')
def list_reports():
    reports = Report.query.order_by(Report.report_date.desc()).all()
    return render_template('report/list.html', reports=reports)

@report_bp.route('/<int:report_id>')
def report_detail(report_id):
    report = Report.query.get_or_404(report_id)
    return render_template('report/detail.html', report=report)

@report_bp.route('/add', methods=['GET', 'POST'])
def add_report():
    if request.method == 'POST':
        try:
            report_date = datetime.strptime(request.form['report_date'], '%Y-%m-%d').date()
        except ValueError:
            flash('日付の形式が正しくありません。YYYY-MM-DD形式で入力してください。', 'error')
            return redirect(url_for('work_report.add_report'))

        if Report.query.filter_by(report_date=report_date).first():
            flash('その日付の日報は既に存在します。', 'error')
            return redirect(url_for('work_report.add_report'))

        new_report = Report(
            report_date=report_date,
            start_scheduled_time=request.form['start_scheduled_time'],
            start_scheduled_tasks=request.form['start_scheduled_tasks'],
            start_goals=request.form['start_goals']
        )
        db.session.add(new_report)
        db.session.commit()
        flash('開始報告が登録されました。', 'success')
        return redirect(url_for('work_report.list_reports'))
    
    return render_template('report/form.html', report=None)


@report_bp.route('/edit/<int:report_id>', methods=['GET', 'POST'])
def edit_report(report_id):
    report = Report.query.get_or_404(report_id)
    if request.method == 'POST':
        report.end_actual_time = request.form['end_actual_time']
        report.end_completed_tasks = request.form['end_completed_tasks']
        report.end_reflection = request.form['end_reflection']
        
        # 開始報告の内容も更新できるようにする
        report.start_scheduled_time = request.form['start_scheduled_time']
        report.start_scheduled_tasks = request.form['start_scheduled_tasks']
        report.start_goals = request.form['start_goals']

        db.session.commit()
        flash('日報が更新されました。', 'success')
        return redirect(url_for('work_report.report_detail', report_id=report.id))

    return render_template('report/form.html', report=report)

@report_bp.route('/delete/<int:report_id>', methods=['POST'])
def delete_report(report_id):
    report = Report.query.get_or_404(report_id)
    db.session.delete(report)
    db.session.commit()
    flash('日報が削除されました。', 'success')
    return redirect(url_for('work_report.list_reports'))