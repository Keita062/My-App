from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime, timedelta
import json
from flask_survey_app.extensions import db
from .models import Report
from sqlalchemy import desc

report_bp = Blueprint(
    'report', 
    __name__,
    template_folder='templates',
    static_folder='static'
)

def get_previous_report(report_date):
    """
    指定された日付より前の、最新の完了報告を持つ日報を取得する
    """
    return Report.query.filter(
        Report.report_date < report_date,
        Report.end_completed_tasks.isnot(None),
        Report.end_completed_tasks != ''
    ).order_by(desc(Report.report_date)).first()

@report_bp.route('/')
def list_reports():
    """日報の一覧を表示"""
    all_reports = Report.query.order_by(Report.report_date.desc()).all()
    # JSON形式のタスクデータをPythonのリストに変換
    for report in all_reports:
        try:
            # start_scheduled_tasksがJSON形式（リスト）か、古いテキスト形式かを判定
            if report.start_scheduled_tasks and report.start_scheduled_tasks.strip().startswith('['):
                report.start_tasks = json.loads(report.start_scheduled_tasks)
            # 古い形式や空の場合でも空のリストを保証
            else:
                report.start_tasks = []
            
            # end_completed_tasksも同様に処理
            if report.end_completed_tasks and report.end_completed_tasks.strip().startswith('['):
                report.end_tasks = json.loads(report.end_completed_tasks)
            else:
                report.end_tasks = []
        except (json.JSONDecodeError, TypeError):
            # 万が一パースに失敗した場合
            report.start_tasks = [{'desc': 'データ形式エラー', 'duration': ''}]
            report.end_tasks = [{'desc': 'データ形式エラー', 'duration': ''}]
            
    return render_template('report/list.html', reports=all_reports)

@report_bp.route('/new', methods=['GET', 'POST'])
def new_report():
    """新しい開始報告を作成するためのルート"""
    if request.method == 'POST':
        report_date_str = request.form['report_date']
        report_date = datetime.strptime(report_date_str, '%Y-%m-%d').date()
        
        # 同じ日付の日報が既に存在するかチェック
        if Report.query.filter_by(report_date=report_date).first():
            flash(f'{report_date.strftime("%Y-%m-%d")}の報告は既に存在します。一覧から編集してください。', 'error')
            return redirect(url_for('report.list_reports'))

        # フォームからタスクリストを作成
        start_tasks = [{'desc': d, 'duration': u} for d, u in zip(request.form.getlist('start_task_descriptions[]'), request.form.getlist('start_task_durations[]')) if d.strip()]
        
        new_report_obj = Report(
            report_date=report_date,
            start_scheduled_time=f"{request.form['start_time']} - {request.form['end_time']}",
            start_scheduled_tasks=json.dumps(start_tasks, ensure_ascii=False),
            start_goals=request.form['goals']
        )
        db.session.add(new_report_obj)
        db.session.commit()
        flash('開始報告を登録しました。', 'success')
        return redirect(url_for('report.list_reports'))
    
    # GETリクエストの場合
    today = datetime.now().date()
    # 前回の完了報告を取得
    previous_report = get_previous_report(today)
    
    return render_template('report/form.html', 
                           form_type='new_start', 
                           report=None, 
                           previous_report=previous_report)

@report_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_report(id):
    """日報の編集（開始・完了報告の両方）"""
    report = Report.query.get_or_404(id)
    
    if request.method == 'POST':
        # --- 開始報告の更新 ---
        report.start_scheduled_time = f"{request.form['start_time']} - {request.form['end_time']}"
        start_tasks_list = [{'desc': d, 'duration': u} for d, u in zip(request.form.getlist('start_task_descriptions[]'), request.form.getlist('start_task_durations[]')) if d.strip()]
        report.start_scheduled_tasks = json.dumps(start_tasks_list, ensure_ascii=False)
        report.start_goals = request.form['goals']

        # --- 完了報告の更新 (入力があれば) ---
        # 完了報告の開始時間が入力されているかで判断
        if request.form.get('end_start_time'):
            report.end_actual_time = f"{request.form['end_start_time']} - {request.form['end_end_time']}"
            end_tasks_list = [{'desc': d, 'duration': u} for d, u in zip(request.form.getlist('end_task_descriptions[]'), request.form.getlist('end_task_durations[]')) if d.strip()]
            report.end_completed_tasks = json.dumps(end_tasks_list, ensure_ascii=False)
            report.end_reflection = request.form['reflection']
        
        db.session.commit()
        flash('日報を更新しました。', 'success')
        return redirect(url_for('report.list_reports'))

    # GETリクエストの場合
    # 前回の完了報告を取得
    previous_report = get_previous_report(report.report_date)
    
    return render_template('report/form.html', 
                           form_type='edit', 
                           report=report, 
                           previous_report=previous_report)

@report_bp.route('/delete/<int:id>', methods=['POST'])
def delete_report(id):
    """日報を削除"""
    report_to_delete = Report.query.get_or_404(id)
    db.session.delete(report_to_delete)
    db.session.commit()
    flash('日報を削除しました。', 'success')
    return redirect(url_for('report.list_reports'))