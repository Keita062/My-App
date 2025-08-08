import os
import json
from flask import Flask, render_template, jsonify, request, url_for
from config import config # 作成したconfig.pyをインポート
from extensions import db # 作成したextensions.pyをインポート

def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'default')

    # メインのテンプレート/静的フォルダを指定してFlaskアプリを初期化 
    app = Flask(
        __name__,
        template_folder='flask_survey_app/templates',
        static_folder='flask_survey_app/static'
    )
    
    # config.pyから設定を読み込む
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # extensions.pyからdbを初期化
    db.init_app(app)

    # --- Blueprintの登録 ---
    # 【変更点】リファクタリング済みのwork_report_appを呼び出す
    from work_report_app.routes import report_bp
    app.register_blueprint(report_bp, url_prefix='/report') # 元のURLプリフィックスを維持 

    # (今後、他のアプリをリファクタリングしたら、ここに追加していく)
    # from todo_app.routes import todo_bp
    # app.register_blueprint(todo_bp, url_prefix='/todo')
    
    # --- ルートと共通機能の登録 ---
    # (この部分は変更なし、run.pyにそのまま残す)
    register_routes(app)
    register_filters(app)
    register_request_handlers(app)

    return app

# --- 以下、共通機能の関数（変更なし、整理しただけ）---

def register_routes(app):
    """ポータルやAPIなど、共通のルートを登録する"""
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/api/events')
    def get_events():
        # TODO: 今後、各アプリをリファクタリングする際に、ここのimportも修正が必要
        from idea_app.models import Idea
        from flask_survey_app.models import Survey
        from work_report_app.models import Report
        from research_app.models import Company
        from todo_app.models import Todo
        
        events = []
        # ... イベント取得ロジックは元のまま ... 
        reports = Report.query.all()
        for report in reports:
            events.append({'title': "【日報】提出済", 'start': report.report_date.isoformat(), 'url': url_for('work_report.list_reports'), 'className': 'event-report'})
        
        return jsonify(events)

def register_filters(app):
    """Jinjaフィルターを登録する"""
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
    """リクエスト毎の処理を登録する"""
    # TODO: log_utilsも将来的には共通化したい
    from flask_survey_app.log_utils import Log

    @app.after_request
    def log_response_info(response):
        if request.path.startswith(('/static', '/api')):
            return response
        
        new_log = Log(ip_address=request.remote_addr, path=request.path, method=request.method)
        db.session.add(new_log)
        db.session.commit()
        return response

# --- アプリケーションの実行 ---
app = create_app()

if __name__ == '__main__':
    with app.app_context():
        # 初回起動時などに、必要に応じてテーブルを作成する
        # db.create_all()
        pass
    app.run(debug=True, host='0.0.0.0', port=5001)