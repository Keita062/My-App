from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime
import json
from flask_survey_app.extensions import db
from .models import Report

report_bp = Blueprint(
    'report', 
    __name__,
    template_folder='templates',
    static_folder='static' # staticフォルダのパスを追加
)

@report_bp.route('/')
def list_reports():
    """日報の一覧を表示"""
    all_reports = Report.query.order_by(Report.report_date.desc()).all()
    for report in all_reports:
        try:
            # 開始報告タスクの処理
            if report.start_scheduled_tasks and report.start_scheduled_tasks.strip().startswith('['):
                report.start_tasks = json.loads(report.start_scheduled_tasks)
            else:
                # 古い形式のデータ（単なるテキスト）を新しい形式に変換
                report.start_tasks = [{'desc': report.start_scheduled_tasks, 'duration': 'N/A'}] if report.start_scheduled_tasks else []

            # 完了報告タスクの処理
            if report.end_completed_tasks and report.end_completed_tasks.strip().startswith('['):
                report.end_tasks = json.loads(report.end_completed_tasks)
            else:
                report.end_tasks = [{'desc': report.end_completed_tasks, 'duration': 'N/A'}] if report.end_completed_tasks else []
        except (json.JSONDecodeError, TypeError):
            # JSONデコードに失敗した場合のフォールバック
            report.start_tasks = [{'desc': 'データ形式エラー', 'duration': ''}]
            report.end_tasks = [{'desc': 'データ形式エラー', 'duration': ''}]

    return render_template('report/list.html', reports=all_reports)

@report_bp.route('/select_type')
def select_type():
    """報告タイプ（開始 or 完了）を選択するページ"""
    # 完了報告がまだされていないレポートのリストを取得
    reports_to_complete = Report.query.filter(Report.end_completed_tasks == None).order_by(Report.report_date.desc()).all()
    return render_template('report/select_type.html', reports_to_complete=reports_to_complete)

@report_bp.route('/new_start', methods=['GET', 'POST'])
def new_start_report():
    """新しい開始報告を作成"""
    if request.method == 'POST':
        report_date_str = request.form['report_date']
        report_date = datetime.strptime(report_date_str, '%Y-%m-%d').date()

        existing_report = Report.query.filter_by(report_date=report_date).first()
        if existing_report:
            flash(f'{report_date_str}の開始報告は既に存在します。', 'error')
            return redirect(url_for('report.select_type'))

        task_descriptions = request.form.getlist('task_descriptions[]')
        task_durations = request.form.getlist('task_durations[]')
        tasks = [{'desc': desc, 'duration': dur} for desc, dur in zip(task_descriptions, task_durations) if desc]
        
        new_report = Report(
            report_date=report_date,
            start_scheduled_time=f"{request.form['start_time']} - {request.form['end_time']}",
            start_scheduled_tasks=json.dumps(tasks, ensure_ascii=False), # JSON文字列として保存
            start_goals=request.form['goals']
        )
        db.session.add(new_report)
        db.session.commit()
        flash(f'{report_date_str}の開始報告を登録しました。', 'success')
        return redirect(url_for('report.list_reports'))
    
    return render_template('report/form.html', form_type='start', report=None)

@report_bp.route('/new_end/<int:id>', methods=['GET', 'POST'])
def new_end_report(id):
    """完了報告を追加"""
    report = Report.query.get_or_404(id)
    if request.method == 'POST':
        task_descriptions = request.form.getlist('task_descriptions[]')
        task_durations = request.form.getlist('task_durations[]')
        tasks = [{'desc': desc, 'duration': dur} for desc, dur in zip(task_descriptions, task_durations) if desc]

        report.end_actual_time = f"{request.form['start_time']} - {request.form['end_time']}"
        report.end_completed_tasks = json.dumps(tasks, ensure_ascii=False) # JSON文字列として保存
        report.end_reflection = request.form['reflection']
        db.session.commit()
        flash(f'{report.report_date.strftime("%Y-%m-%d")}の完了報告を登録しました。', 'success')
        return redirect(url_for('report.list_reports'))

    return render_template('report/form.html', form_type='end', report=report)

@report_bp.route('/delete/<int:id>', methods=['POST'])
def delete_report(id):
    report_to_delete = Report.query.get_or_404(id)
    db.session.delete(report_to_delete)
    db.session.commit()
    flash(f'{report_to_delete.report_date.strftime("%Y-%m-%d")}の日報を削除しました。', 'success')
    return redirect(url_for('report.list_reports'))