# main_app.py
import os
# 【修正】url_for をインポートリストに追加
from flask import Flask, render_template, request, jsonify, url_for
from datetime import datetime

# --- 各アプリケーションのモジュールをインポート ---
from flask_survey_app.extensions import db
# 【修正】Surveyモデルを正しい場所からインポート
from flask_survey_app.app import survey_bp, Survey 
from flask_survey_app.log_utils import Log

from work_report_app.app import report_bp 
from work_report_app.models import Report

from idea_app.app import idea_bp
from idea_app.models import Idea

from payroll_app.app import payroll_bp
from payroll_app import models as payroll_models

from research_app.app import research_bp
from research_app.models import Company

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

    # --- 各アプリのディレクトリパスを定義 ---
    survey_app_dir = os.path.join(basedir, 'flask_survey_app')
    report_app_dir = os.path.join(basedir, 'work_report_app')
    idea_app_dir = os.path.join(basedir, 'idea_app')
    payroll_app_dir = os.path.join(basedir, 'payroll_app')
    research_app_dir = os.path.join(basedir, 'research_app')

    # --- データベース設定 ---
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(survey_app_dir, 'survey.db')
    app.config['SQLALCHEMY_BINDS'] = {
        'logs': 'sqlite:///' + os.path.join(survey_app_dir, 'log.db'),
        'report': 'sqlite:///' + os.path.join(report_app_dir, 'report.db'),
        'idea': 'sqlite:///' + os.path.join(idea_app_dir, 'idea.db'),
        'payroll': 'sqlite:///' + os.path.join(payroll_app_dir, 'payroll.db'),
        'research': 'sqlite:///' + os.path.join(research_app_dir, 'research.db')
    }
    
    # --- 拡張機能の初期化 ---
    db.init_app(app)

    # --- Blueprintの登録 ---
    app.register_blueprint(survey_bp, url_prefix='/survey') 
    app.register_blueprint(report_bp, url_prefix='/report')
    app.register_blueprint(idea_bp, url_prefix='/idea')
    app.register_blueprint(payroll_bp, url_prefix='/payroll')
    app.register_blueprint(research_bp, url_prefix='/research')
    
    # --- ルート定義 ---
    @app.route('/')
    def index():
        """ポータルページを表示"""
        return render_template('index.html')

    @app.route('/api/events')
    def get_events():
        """カレンダー用のイベントデータをJSONで返すAPI"""
        events = []
        
        # 1. アイディアフォームのイベント
        ideas = Idea.query.all()
        for idea in ideas:
            events.append({
                'title': f"【ｱｲﾃﾞｨｱ】{idea.title}",
                'start': idea.creation_date.isoformat(),
                'url': url_for('idea.edit_idea', id=idea.id),
                'className': 'event-idea'
            })
            if idea.due_date:
                events.append({
                    'title': f"【目標】{idea.title}",
                    'start': idea.due_date.isoformat(),
                    'url': url_for('idea.edit_idea', id=idea.id),
                    'className': 'event-idea-due'
                })

        # 2. ES記入フォームの締切
        surveys = Survey.query.all()
        for survey in surveys:
            if survey.deadline:
                events.append({
                    'title': f"【ES締切】{survey.company_name}",
                    'start': survey.deadline.isoformat(),
                    'url': url_for('survey.detail_survey', id=survey.id),
                    'className': 'event-survey'
                })
        
        # 3. 日報の報告日
        reports = Report.query.all()
        for report in reports:
            events.append({
                'title': "【日報】提出済",
                'start': report.report_date.isoformat(),
                'url': url_for('report.list_reports'),
                'className': 'event-report'
            })
            
        # 4. 企業研究ツールのイベント
        companies = Company.query.all()
        for company in companies:
            if company.es_deadline:
                events.append({
                    'title': f"【ES締切】{company.company_name}",
                    'start': company.es_deadline.isoformat(),
                    'url': url_for('research.detail_company', id=company.id),
                    'className': 'event-survey'
                })
            if company.interview_date:
                events.append({
                    'title': f"【面接】{company.company_name}",
                    'start': company.interview_date.isoformat(),
                    'url': url_for('research.detail_company', id=company.id),
                    'className': 'event-interview'
                })

        return jsonify(events)

    @app.after_request
    def log_response_info(response):
        """アクセスログを記録する"""
        if request.path.startswith('/static') or request.path.startswith('/api'):
            return response
            
        new_log = Log(
            ip_address=request.remote_addr,
            path=request.path,
            method=request.method
        )
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