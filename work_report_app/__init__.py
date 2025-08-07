from flask import Flask
from config import config
from extensions import db

def create_app(config_name='default'):
    """アプリケーションファクトリ関数"""
    app = Flask(__name__, instance_relative_config=True)

    # config.py から設定をロード
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # config.pyのDATABASE_URIS辞書から、'work_report'用のDB URIを設定
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['DATABASE_URIS']['work_report']

    # データベースをアプリケーションに紐付け
    db.init_app(app)

    # Blueprint をアプリケーションに登録
    from .routes import report_bp
    app.register_blueprint(report_bp, url_prefix='/work_report')

    return app