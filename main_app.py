import os
from flask import Flask, render_template, request, jsonify, url_for
from datetime import datetime

# --- 既存のimport文 ---
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
from memo_app.app import memo_bp
from memo_app.models import Memo

# --- ここから修正・追加 ---
# 1. 分析アプリのBlueprintをインポート
from analytics_app.views import analytics_bp

def create_app():
    app = Flask(
        __name__,
        # メインのテンプレート・静的ファイルフォルダをプロジェクトルート直下に設定
        template_folder='templates',
        static_folder='static'
    )

    # --- アプリケーションの設定 ---
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.secret_key = 'my-super-secret-key-for-development'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # --- 各アプリのディレクトリパス定義 ---
    survey_app_dir = os.path.join(basedir, 'flask_survey_app')
    report_app_dir = os.path.join(basedir, 'work_report_app')
    idea_app_dir = os.path.join(basedir, 'idea_app')
    payroll_app_dir = os.path.join(basedir, 'payroll_app')
    research_app_dir = os.path.join(basedir, 'research_app')
    memo_app_dir = os.path.join(basedir, 'memo_app')
    # 2. 分析アプリのディレクトリパスを追加
    analytics_app_dir = os.path.join(basedir, 'analytics_app')


    # --- データベース設定 ---
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(survey_app_dir, 'survey.db')
    app.config['SQLALCHEMY_BINDS'] = {
        'logs': 'sqlite:///' + os.path.join(survey_app_dir, 'log.db'),
        'report': 'sqlite:///' + os.path.join(report_app_dir, 'report.db'),
        'idea': 'sqlite:///' + os.path.join(idea_app_dir, 'idea.db'),
        'payroll': 'sqlite:///' + os.path.join(payroll_app_dir, 'payroll.db'),
        'research': 'sqlite:///' + os.path.join(research_app_dir, 'research.db'),
        'memo': 'sqlite:///' + os.path.join(memo_app_dir, 'memo.db'),
        # 3. analyticsのDBパスを追加
        'analytics': 'sqlite:///' + os.path.join(analytics_app_dir, 'analytics.db')
    }

    # --- 分析アプリ用の追加設定 ---
    # 4. ファイルアップロード関連の設定を追加
    app.config['UPLOAD_FOLDER'] = os.path.join(analytics_app_dir, 'uploads')
    app.config['ALLOWED_EXTENSIONS'] = {'csv', 'xlsx', 'xls'}
    app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB

    # UPLOAD_FOLDERが存在しない場合は作成
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    # --- DBの初期化 ---
    db.init_app(app)

    # --- Blueprintの登録 ---
    app.register_blueprint(survey_bp, url_prefix='/survey')
    app.register_blueprint(report_bp, url_prefix='/report')
    app.register_blueprint(idea_bp, url_prefix='/idea')
    app.register_blueprint(payroll_bp, url_prefix='/payroll')
    app.register_blueprint(research_bp, url_prefix='/research')
    app.register_blueprint(memo_bp, url_prefix='/memo')
    app.register_blueprint(analytics_bp, url_prefix='/analytics')


    # --- ルートURLの定義 ---
    @app.route('/')
    def index():
        return "<h1>MY-APP Portal</h1><p><a href='/analytics'>分析ダッシュボードへ</a></p>" # 仮のポータル

    # (既存の get_events, log_response_info はそのまま)
    @app.route('/api/events')
    def get_events():
        # ... (既存のコード)
        events = []
        return jsonify(events)

    @app.after_request
    def log_response_info(response):
        # ... (既存のコード)
        return response

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        # 全てのデータベースに対してテーブルを作成
        db.create_all()
    # ポート番号は元の5001に戻します
    app.run(debug=True, host='0.0.0.0', port=5001)