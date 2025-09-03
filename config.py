import os
from pathlib import Path  # pathlibをインポート

# pathlibを使用して、より確実にプロジェクトのルートディレクトリのパスを取得
basedir = Path(__file__).resolve().parent

class Config:
    """ベースとなる設定クラス"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'my-super-secret-key-for-development'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # アップロードフォルダのパスもpathlibで設定
    UPLOAD_FOLDER = basedir / 'instance' / 'uploads'

    @staticmethod
    def init_app(app):
        """アプリケーション初期化時に共通処理を実行"""
        # instanceフォルダが存在しない場合に自動で作成する
        instance_folder = basedir / 'instance'
        instance_folder.mkdir(exist_ok=True)

class DevelopmentConfig(Config):
    """開発環境用の設定"""
    DEBUG = True
    
    # instanceフォルダへのパスを定義
    instance_path = basedir / 'instance'
    
    # メインのDB。str()で正しいパス文字列に変換
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + str(instance_path / 'survey.db')
    
    # 複数のデータベースの場所を 'BINDS' として一元管理
    SQLALCHEMY_BINDS = {
        'survey':    'sqlite:///' + str(instance_path / 'survey.db'),
        'logs':      'sqlite:///' + str(instance_path / 'log.db'),
        'report':    'sqlite:///' + str(instance_path / 'report.db'),
        'idea':      'sqlite:///' + str(instance_path / 'idea.db'),
        'payroll':   'sqlite:///' + str(instance_path / 'payroll.db'),
        'research':  'sqlite:///' + str(instance_path / 'research.db'),
        'memo':      'sqlite:///' + str(instance_path / 'memo.db'),
        'todo':      'sqlite:///' + str(instance_path / 'todo.db'),
        'budget':    'sqlite:///' + str(instance_path / 'budget.db'),
        'dashboard': 'sqlite:///' + str(instance_path / 'dashboard.db')
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