# main_app.py
import os
from flask import Flask, render_template, request
from datetime import datetime

from flask_survey_app.extensions import db
from flask_survey_app.app import survey_bp
from flask_survey_app.log_utils import Log
from work_report_app.app import report_bp 
from work_report_app import models as report_models
from idea_app.app import idea_bp
from idea_app import models as idea_models

# 【追加】給与計算アプリのBlueprintとモデルをインポート
from payroll_app.app import payroll_bp
from payroll_app import models as payroll_models

def create_app():
    app = Flask(
        __name__, 
        template_folder='flask_survey_app/templates',
        static_folder='flask_survey_app/static'
    )

    # --- アプリケーションの設定 ---
    basedir = os.path.abspath(os.path.dirname(__file__))
    survey_app_dir = os.path.join(basedir, 'flask_survey_app')
    report_app_dir = os.path.join(basedir, 'work_report_app')
    idea_app_dir = os.path.join(basedir, 'idea_app')
    payroll_app_dir = os.path.join(basedir, 'payroll_app')

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(survey_app_dir, 'survey.db')  
    app.config['SQLALCHEMY_BINDS'] = {
        'logs': 'sqlite:///' + os.path.join(survey_app_dir, 'log.db'),
        'report': 'sqlite:///' + os.path.join(report_app_dir, 'report.db'),
        'idea': 'sqlite:///' + os.path.join(idea_app_dir, 'idea.db'),
        'payroll': 'sqlite:///' + os.path.join(payroll_app_dir, 'payroll.db')
    }
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    # --- Blueprintの登録 ---
    app.register_blueprint(survey_bp, url_prefix='/survey') 
    app.register_blueprint(report_bp, url_prefix='/report')
    app.register_blueprint(idea_bp, url_prefix='/idea')
    app.register_blueprint(payroll_bp, url_prefix='/payroll')
    
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.after_request
    def log_response_info(response):
        return response

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5001)