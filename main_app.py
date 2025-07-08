import os
from flask import Flask, render_template, request
from datetime import datetime

# 必要なモジュールをインポート
from flask_survey_app.extensions import db
from flask_survey_app.app import survey_bp
from flask_survey_app.log_utils import Log

def create_app():
    app = Flask(
        __name__, 
        template_folder='flask_survey_app/templates',
        static_folder='flask_survey_app/static'
    )

    # --- アプリケーションの設定 ---
    basedir = os.path.abspath(os.path.dirname(__file__))
    survey_app_dir = os.path.join(basedir, 'flask_survey_app')

    # 1. アンケート用データベース (survey.db) の設定
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(survey_app_dir, 'survey.db')
    
    # 2. ログ用データベース (log.db) の設定
    app.config['SQLALCHEMY_BINDS'] = {
        'logs': 'sqlite:///' + os.path.join(survey_app_dir, 'log.db')
    }
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # --- 拡張機能の初期化 ---
    db.init_app(app)

    # --- Blueprintの登録 ---
    app.register_blueprint(survey_bp, url_prefix='/survey') 
    
    # --- ホームページのルート ---
    @app.route('/')
    def index():
        return render_template('index.html')


    @app.after_request
    def log_response_info(response):
        # staticファイルへのリクエストはログの対象外にする
        if request.path.startswith('/static'):
            return response
            
        # 新しいLogオブジェクトを作成
        new_log = Log(
            ip_address=request.remote_addr,
            path=request.path,
            method=request.method
        )
        # データベースセッションに追加してコミット
        with app.app_context():
            db.session.add(new_log)
            db.session.commit()
        
        return response

    return app

# --- アプリケーションの実行 ---
# このファイルが直接実行された場合にのみ、サーバーを起動する
if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        # データベースとテーブルを作成
        db.create_all()
    # デバッグモードでアプリケーションを実行
    app.run(debug=True, host='0.0.0.0', port=5001)