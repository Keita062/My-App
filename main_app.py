import os
from flask import Flask, render_template
# 'flask_survey_app'フォルダの中にあるextensionsからdbをインポート
from flask_survey_app.extensions import db
# 'flask_survey_app'フォルダの中にあるappからsurvey_bpをインポート
from flask_survey_app.app import survey_bp

def create_app():
    # Flaskアプリケーションを作成
    # テンプレートフォルダの場所を正しく指定
    app = Flask(__name__, template_folder='flask_survey_app/templates')

    # --- アプリケーションの設定 ---
    basedir = os.path.abspath(os.path.dirname(__file__))
    # データベース名をスクリーンショットに合わせて 'survey.db' に修正
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'survey.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # --- 拡張機能の初期化 ---
    db.init_app(app)

    # --- Blueprintの登録 ---
    # アンケートアプリを '/survey' というURLで登録
    app.register_blueprint(survey_bp, url_prefix='/survey') 
    
    # --- ホームページのルート ---
    @app.route('/')
    def index():
        # アプリケーション選択用のトップページを表示
        return render_template('index.html')

    # --- データベースの作成 ---
    with app.app_context():
        db.create_all()

    return app

# --- アプリケーションの実行 ---
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
