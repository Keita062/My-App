import os
import json
from flask import Flask, render_template, jsonify, request, url_for
from config import config
from extensions import db
import click # Flaskのコマンド機能のためにインポート

def create_app(config_name=None):
    """
    アプリケーションファクトリ関数。
    この関数がFlaskアプリケーションのインスタンスを生成し、
    各種設定や拡張機能、Blueprintを登録します。
    """
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'default')

    app = Flask(
        __name__,
        # 注意: ポータルページ(index.html)が flask_survey_app にあるため、
        # そのパスを基準にしています。
        template_folder='flask_survey_app/templates',
        static_folder='flask_survey_app/static'
    )
    
    # config.pyから設定を読み込みます
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # extensions.pyからdbを初期化し、アプリケーションに紐付けます
    db.init_app(app)

    # --- すべてのBlueprintをここで登録 ---
    # 各サブアプリケーションの`routes.py`からBlueprintオブジェクトをインポートし、
    # URLの接頭辞(prefix)と共にアプリケーションに登録します。
    
    from flask_survey_app.routes import survey_bp
    app.register_blueprint(survey_bp, url_prefix='/survey')
    
    from work_report_app.routes import report_bp
    app.register_blueprint(report_bp, url_prefix='/report')

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

    from budget_app.routes import budget_bp
    app.register_blueprint(budget_bp, url_prefix='/budget')


    # --- 共通機能の登録 ---
    # 特定のアプリケーションに属さない、全体で共通の機能を登録します。
    register_routes(app)
    register_filters(app)
    register_request_handlers(app)
    
    # --- カスタムコマンドの登録 ---
    # データベース初期化のためのコマンドを登録します。
    @app.cli.command("init-db")
    def init_db_command():
        """データベースのテーブルをすべて作成する"""
        with app.app_context():
            # models.pyで定義された全てのテーブルをデータベース内に作成
            db.create_all()
        click.echo("Initialized the database.")

    return app

# -----------------------------------------------------------------------------
# 以下は、アプリケーションの共通機能を定義するヘルパー関数です。
# -----------------------------------------------------------------------------

def register_routes(app):
    """ポータルページや共通APIなど、特定のアプリに属さないルートを登録"""
    
    @app.route('/')
    def index():
        """ポータルページを表示"""
        return render_template('index.html')

    @app.route('/api/events')
    def get_events():
        """カレンダー用のイベントデータをJSONで返すAPI"""
        # 必要なモデルをインポート
        from idea_app.models import Idea
        from flask_survey_app.models import Survey
        from work_report_app.models import Report
        from research_app.models import Company, SelectionEvent
        from todo_app.models import Todo
        
        events = []
        # ここに、元のmain_app.pyにあったイベント取得ロジックをすべて記述
        # (例)
        reports = Report.query.all()
        for report in reports:
            events.append({
                'title': "【日報】提出済", 
                'start': report.report_date.isoformat(), 
                'url': url_for('work_report.list_reports'), 
                'className': 'event-report'
            })
        # ... 他のすべてのイベント取得ロジック ...
        
        return jsonify(events)

def register_filters(app):
    """テンプレートで使うカスタムフィルターを登録"""
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
    """リクエスト毎の共通処理（アクセスログなど）を登録"""
    from flask_survey_app.models import Log

    @app.after_request
    def log_response_info(response):
        if request.path.startswith(('/static', '/api')):
            return response
        
        new_log = Log(ip_address=request.remote_addr, path=request.path, method=request.method)
        db.session.add(new_log)
        db.session.commit()
        
        return response

# --- アプリケーションの実行 ---
# create_app()を呼び出して、Flaskアプリケーションインスタンスを作成
app = create_app()

if __name__ == '__main__':
    # `python run.py`で直接実行された場合に、開発用サーバーを起動
    app.run(debug=True, host='0.0.0.0', port=5001)