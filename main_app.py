import os
from flask import Flask, render_template, request, jsonify, url_for
from datetime import datetime

# (既存のimport文)
from flask_survey_app.extensions import db
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

# 【修正】メモツールのBlueprintとモデルをインポート
from memo_app.app import memo_bp
from memo_app.models import Memo

def create_app():
    app = Flask(
        __name__, 
        template_folder='flask_survey_app/templates',
        static_folder='flask_survey_app/static'
    )

    # --- アプリケーションの設定 ---
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.secret_key = 'my-super-secret-key-for-development'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # (各アプリのディレクトリパス定義)
    survey_app_dir = os.path.join(basedir, 'flask_survey_app')
    report_app_dir = os.path.join(basedir, 'work_report_app')
    idea_app_dir = os.path.join(basedir, 'idea_app')
    payroll_app_dir = os.path.join(basedir, 'payroll_app')
    research_app_dir = os.path.join(basedir, 'research_app')
    memo_app_dir = os.path.join(basedir, 'memo_app')

    # --- データベース設定 ---
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(survey_app_dir, 'survey.db')
    app.config['SQLALCHEMY_BINDS'] = {
        'logs': 'sqlite:///' + os.path.join(survey_app_dir, 'log.db'),
        'report': 'sqlite:///' + os.path.join(report_app_dir, 'report.db'),
        'idea': 'sqlite:///' + os.path.join(idea_app_dir, 'idea.db'),
        'payroll': 'sqlite:///' + os.path.join(payroll_app_dir, 'payroll.db'),
        'research': 'sqlite:///' + os.path.join(research_app_dir, 'research.db'),
        'memo': 'sqlite:///' + os.path.join(memo_app_dir, 'memo.db') # 【修正】
    }
    
    db.init_app(app)

    # --- Blueprintの登録 ---
    app.register_blueprint(survey_bp, url_prefix='/survey') 
    app.register_blueprint(report_bp, url_prefix='/report')
    app.register_blueprint(idea_bp, url_prefix='/idea')
    app.register_blueprint(payroll_bp, url_prefix='/payroll')
    app.register_blueprint(research_bp, url_prefix='/research')
    app.register_blueprint(memo_bp, url_prefix='/memo') # 【修正】
    
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/api/events')
    def get_events():
        # ...
        return jsonify(events)

    @app.after_request
    def log_response_info(response):
        # ...
        return response

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5001)