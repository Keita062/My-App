import os
from flask import Flask, render_template, request
from datetime import datetime
from flask_survey_app.extensions import db
from flask_survey_app.app import survey_bp
from flask_survey_app.log_utils import Log
from work_report_app.app import report_bp 
from work_report_app import models

def create_app():
    """
    Flaskアプリケーションのファクトリ関数
    """
    app = Flask(
        __name__, 
        template_folder='flask_survey_app/templates',
        static_folder='flask_survey_app/static'
    )

    # --- アプリケーションの設定 ---
    basedir = os.path.abspath(os.path.dirname(__file__))
    survey_app_dir = os.path.join(basedir, 'flask_survey_app')
    report_app_dir = os.path.join(basedir, 'work_report_app')

    # 1. アンケート用データベース (survey.db) の設定
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(survey_app_dir, 'survey.db')
    app.config['SQLALCHEMY_BINDS'] = {
        'logs': 'sqlite:///' + os.path.join(survey_app_dir, 'log.db'),
        'report': 'sqlite:///' + os.path.join(report_app_dir, 'report.db')
    }
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # --- 拡張機能の初期化 ---
    db.init_app(app)

    # --- Blueprintの登録 ---
    app.register_blueprint(survey_bp, url_prefix='/survey') 
    app.register_blueprint(report_bp, url_prefix='/report')
    
    # --- ホームページのルート ---
    @app.route('/')
    def index():
        """
        ポータルトップページを表示
        """
        return render_template('index.html')

    # --- リクエスト後にログを記録する関数 ---
    @app.after_request
    def log_response_info(response):
        """
        リクエストの情報をログデータベースに記録する
        """
        if request.path.startswith('/static'):
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