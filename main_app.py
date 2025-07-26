# main_app.py
import os
from flask import Flask, render_template, request, jsonify, url_for
from datetime import datetime

# --- 各アプリケーションのモジュールをインポート ---
# 拡張機能
from flask_survey_app.extensions import db

# アプリケーション1: ES記入フォーム
from flask_survey_app.app import survey_bp, Survey 

# アプリケーション2: REHATCH日報
from work_report_app.app import report_bp 
from work_report_app.models import Report

# アプリケーション3: アイディアフォーム
from idea_app.app import idea_bp
from idea_app.models import Idea

# アプリケーション4: 給与計算アプリ
from payroll_app.app import payroll_bp
from payroll_app import models as payroll_models

# アプリケーション5: 企業研究ツール
from research_app.app import research_bp
from research_app.models import Company, SelectionEvent

# アプリケーション6: メモツール
from memo_app.app import memo_bp
from memo_app.models import Memo

# アプリケーション7: 分析ダッシュボード
from dashboard_app.app import dashboard_bp

# アプリケーション8: ToDoリスト
from todo_app.app import todo_bp
from todo_app.models import Todo

# アプリケーション9: 予算調整
from budget_app.app import budget_bp
from budget_app.models import Client, Budget

# 共通機能: ログ
from flask_survey_app.log_utils import Log

def create_app():
    """
    Flaskアプリケーションのファクトリ関数
    """
    app = Flask(
        __name__, 
        template_folder='flask_survey_app/templates',
        static_folder='flask_survey_app/static'
    )

    # --- アプリケーションの基本設定 ---
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.secret_key = 'my-super-secret-key-for-development'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'dashboard_app', 'uploads')

    # --- 各アプリのディレクトリパスを定義 ---
    survey_app_dir = os.path.join(basedir, 'flask_survey_app')
    report_app_dir = os.path.join(basedir, 'work_report_app')
    idea_app_dir = os.path.join(basedir, 'idea_app')
    payroll_app_dir = os.path.join(basedir, 'payroll_app')
    research_app_dir = os.path.join(basedir, 'research_app')
    memo_app_dir = os.path.join(basedir, 'memo_app')
    todo_app_dir = os.path.join(basedir, 'todo_app')
    budget_app_dir = os.path.join(basedir, 'budget_app')


    # --- データベース設定 ---
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(survey_app_dir, 'survey.db')
    app.config['SQLALCHEMY_BINDS'] = {
        'logs': 'sqlite:///' + os.path.join(survey_app_dir, 'log.db'),
        'report': 'sqlite:///' + os.path.join(report_app_dir, 'report.db'),
        'idea': 'sqlite:///' + os.path.join(idea_app_dir, 'idea.db'),
        'payroll': 'sqlite:///' + os.path.join(payroll_app_dir, 'payroll.db'),
        'research': 'sqlite:///' + os.path.join(research_app_dir, 'research.db'),
        'memo': 'sqlite:///' + os.path.join(memo_app_dir, 'memo.db'),
        'todo': 'sqlite:///' + os.path.join(todo_app_dir, 'todo.db'),
        'budget': 'sqlite:///' + os.path.join(budget_app_dir, 'budget.db')
    }
    
    # --- 拡張機能の初期化 ---
    db.init_app(app)

    # --- Blueprintの登録 ---
    app.register_blueprint(survey_bp, url_prefix='/survey') 
    app.register_blueprint(report_bp, url_prefix='/report')
    app.register_blueprint(idea_bp, url_prefix='/idea')
    app.register_blueprint(payroll_bp, url_prefix='/payroll')
    app.register_blueprint(research_bp, url_prefix='/research')
    app.register_blueprint(memo_bp, url_prefix='/memo')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(todo_bp, url_prefix='/todo')
    app.register_blueprint(budget_bp, url_prefix='/budget')
    
    # --- ルート定義 ---
    @app.route('/')
    def index():
        """ポータルページを表示"""
        return render_template('index.html')

    @app.route('/api/events')
    def get_events():
        """カレンダー用のイベントデータをJSONで返すAPI"""
        events = []
        
        # (既存のイベント取得ロジックは省略)

        # ToDoリストの期日
        tasks = Todo.query.filter(Todo.due_date.isnot(None)).all()
        for task in tasks:
            events.append({
                'title': f"【ToDo】{task.content}",
                'start': task.due_date.isoformat(),
                'url': url_for('todo.list_tasks'),
                'className': 'event-todo'
            })

        return jsonify(events)

    @app.after_request
    def log_response_info(response):
        """アクセスログを記録する"""
        if request.path.startswith(('/static', '/api')):
            return response
            
        new_log = Log(ip_address=request.remote_addr, path=request.path, method=request.method)
        with app.app_context():
            db.session.add(new_log)
            db.session.commit()
        
        return response

    return app

# --- アプリケーションの実行 ---
if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5001)