import os
from flask import Flask, render_template
from flask_survey_app.extensions import db
from flask_survey_app.app import survey_bp

def create_app():
    app = Flask(__name__, template_folder='flask_survey_app/templates')

    # --- アプリケーションの設定 ---
    basedir = os.path.abspath(os.path.dirname(__file__))
    
    # 【変更】データベースファイルのパスを、データが格納されている
    # 'flask_survey_app' フォルダ内の 'survey.db' を指すように修正します。
    survey_app_dir = os.path.join(basedir, 'flask_survey_app')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(survey_app_dir, 'survey.db')
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # --- 拡張機能の初期化 ---
    db.init_app(app)

    # --- Blueprintの登録 ---
    app.register_blueprint(survey_bp, url_prefix='/survey') 
    
    # --- ホームページのルート ---
    @app.route('/')
    def index():
        return render_template('index.html')

    # --- データベースの作成 ---
    # この処理は、もしDBファイルがなくてもエラーにならないようにするため、そのままにします。
    with app.app_context():
        db.create_all()

    return app

# --- アプリケーションの実行 ---
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
