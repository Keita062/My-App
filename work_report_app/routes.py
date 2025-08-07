from flask import Blueprint, render_template, request, redirect, url_for, flash
from .models import Report
from extensions import db
from datetime import datetime

# 'work_report' という名前の Blueprint を作成
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
        # 日付文字列をdateオブジェクトに変換
        try:
            report_date = datetime.strptime(request.form['report_date'], '%Y-%m-%d').date()
        except ValueError:
            flash('日付の形式が正しくありません。YYYY-MM-DD形式で入力してください。', 'error')
            return redirect(url_for('work_report.add_report'))

        # 同じ日付のレポートが既に存在しないかチェック
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
    
    return render_template('report/form.html')


@report_bp.route('/edit/<int:report_id>', methods=['GET', 'POST'])
def edit_report(report_id):
    report = Report.query.get_or_404(report_id)
    if request.method == 'POST':
        # こちらは完了報告の更新を想定
        report.end_actual_time = request.form['end_actual_time']
        report.end_completed_tasks = request.form['end_completed_tasks']
        report.end_reflection = request.form['end_reflection']
        
        db.session.commit()
        flash('完了報告が更新されました。', 'success')
        return redirect(url_for('work_report.report_detail', report_id=report.id))

    # 既存のデータをフォームに渡す
    return render_template('report/form.html', report=report)

@report_bp.route('/delete/<int:report_id>', methods=['POST'])
def delete_report(report_id):
    report = Report.query.get_or_404(report_id)
    db.session.delete(report)
    db.session.commit()
    flash('日報が削除されました。', 'success')
    return redirect(url_for('work_report.list_reports'))