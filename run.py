import os
import json
from flask import Flask, render_template, jsonify, request, url_for
from config import config
from extensions import db
import click # Flaskのコマンド機能のためにインポート

def create_app(config_name=None):
    """
    アプリケーションファクトリ関数。
    """
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'default')

    app = Flask(
        __name__,
        template_folder='flask_survey_app/templates',
        static_folder='flask_survey_app/static'
    )

    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.init_app(app)

    # --- Blueprintの登録 ---
    from flask_survey_app.routes import survey_bp
    app.register_blueprint(survey_bp, url_prefix='/survey')

    # from work_report_app.routes import report_bp
    # app.register_blueprint(report_bp, url_prefix='/report')

    from todo_app.routes import todo_bp
    app.register_blueprint(todo_bp, url_prefix='/todo')

    from idea_app.routes import idea_bp
    app.register_blueprint(idea_bp, url_prefix='/idea')

    from payroll_app.routes import payroll_bp
    app.register_blueprint(payroll_bp, url_prefix='/payroll')

    from research_app.routes import research_bp
    app.register_blueprint(research_bp, url_prefix='/research')

    from memo_app.routes import memo_bp
    app.register_blueprint(memo_bp, url_prefix='/memo')

    from dashboard_app.routes import dashboard_bp
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')

    # from budget_app.routes import budget_bp
    # app.register_blueprint(budget_bp, url_prefix='/budget')


    # --- 共通機能の登録 ---
    register_routes(app)
    register_filters(app)
    register_request_handlers(app)

    # --- カスタムコマンドの登録 ---
    @app.cli.command("init-db")
    def init_db_command():
        """データベースのテーブルをすべて作成する"""
        from flask_survey_app import models
        # from work_report_app import models
        from todo_app import models
        from idea_app import models
        from payroll_app import models
        from research_app import models
        from memo_app import models
        from dashboard_app import models
        # from budget_app import models

        with app.app_context():
            # --- ★★★デバッグコード：データベースのパスをターミナルに表示★★★ ---
            click.echo("--- Attempting to create databases at the following locations: ---")
            if 'SQLALCHEMY_DATABASE_URI' in app.config:
                click.echo(f"Default DB: {app.config['SQLALCHEMY_DATABASE_URI']}")
            if 'SQLALCHEMY_BINDS' in app.config:
                for bind, uri in app.config['SQLALCHEMY_BINDS'].items():
                    click.echo(f"Bind '{bind}': {uri}")
            click.echo("------------------------------------------------------------------")
            # --- ★★★デバッグコードここまで★★★ ---

            db.create_all()
        click.echo("Initialized the database.")

    return app

def register_routes(app):
    @app.route('/')
    def index():
        return render_template('index.html')
    @app.route('/api/events')
    def get_events():
        from idea_app.models import Idea
        from flask_survey_app.models import Survey
        # from work_report_app.models import Report
        from research_app.models import Company, SelectionEvent
        from todo_app.models import Todo
        events = []
        # reports = Report.query.all()
        # for report in reports:
        #     events.append({
        #         'title': "【日報】提出済", 
        #         'start': report.report_date.isoformat(), 
        #         'url': url_for('work_report.list_reports'), 
        #         'className': 'event-report'
        #     })
        return jsonify(events)

def register_filters(app):
    @app.template_filter('fromjson')
    def fromjson_filter(value):
        if not isinstance(value, str): return []
        try: return json.loads(value)
        except (json.JSONDecodeError, TypeError): return []

    @app.template_filter('toLocaleString')
    def to_locale_string_filter(value):
        if isinstance(value, (int, float)): return f"{value:,}"
        return value

def register_request_handlers(app):
    # from flask_survey_app.models import Log
    # @app.after_request
    # def log_response_info(response):
    #     if request.path.startswith(('/static', '/api')):
    #         return response
    #     new_log = Log(ip_address=request.remote_addr, path=request.path, method=request.method)
    #     db.session.add(new_log)
    #     db.session.commit()
    #     return response
    pass

# --- アプリケーションの実行 ---
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)