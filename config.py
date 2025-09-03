import os
from pathlib import Path

# データベースなどを保存する場所を、ユーザーのホームディレクトリに設定
# これにより、Cドライブ直下への書き込み権限の問題を完全に回避します
instance_folder = Path.home() / 'My-App-Data'

class Config:
    """ベースとなる設定クラス"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'my-super-secret-key-for-development'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # アップロードフォルダのパスも定義
    UPLOAD_FOLDER = instance_folder / 'uploads'

    @staticmethod
    def init_app(app):
        """アプリケーション初期化時に共通処理を実行"""
        # instanceフォルダが存在しない場合に自動で作成する
        instance_folder.mkdir(exist_ok=True)
        (instance_folder / 'uploads').mkdir(exist_ok=True)

class DevelopmentConfig(Config):
    """開発環境用の設定"""
    DEBUG = True

    # メインのDBのパスを定義
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + str(instance_folder / 'survey.db')

    # 複数のデータベースの場所を 'BINDS' として一元管理
    SQLALCHEMY_BINDS = {
        'survey':    'sqlite:///' + str(instance_folder / 'survey.db'),
        'logs':      'sqlite:///' + str(instance_folder / 'log.db'),
        'report':    'sqlite:///' + str(instance_folder / 'report.db'),
        'idea':      'sqlite:///' + str(instance_folder / 'idea.db'),
        'payroll':   'sqlite:///' + str(instance_folder / 'payroll.db'),
        'research':  'sqlite:///' + str(instance_folder / 'research.db'),
        'memo':      'sqlite:///' + str(instance_folder / 'memo.db'),
        'todo':      'sqlite:///' + str(instance_folder / 'todo.db'),
        'budget':    'sqlite:///' + str(instance_folder / 'budget.db'),
        'dashboard': 'sqlite:///' + str(instance_folder / 'dashboard.db')
    }

class ProductionConfig(Config):
    """本番環境用の設定"""
    DEBUG = False
    # (本番用の設定はここに記述)

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}