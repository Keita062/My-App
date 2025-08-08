import os

# プロジェクトのルートディレクトリのパスを取得
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """ベースとなる設定クラス"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'my-super-secret-key-for-development'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # アップロードフォルダの保存先も、安全なinstanceフォルダ配下に設定
    UPLOAD_FOLDER = os.path.join(basedir, 'instance', 'uploads')

    @staticmethod
    def init_app(app):
        # アプリケーション初期化時の共通処理（今回はなし）
        pass

class DevelopmentConfig(Config):
    """開発環境用の設定"""
    DEBUG = True
    
    # メインとなるDB（デフォルト）の場所を設定
    # 元々 survey.db だったものを指定 
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(basedir, 'instance', 'survey.db')}"
    
    # 複数のデータベースの場所を 'BINDS' として一元管理 
    SQLALCHEMY_BINDS = {
        'logs':       f"sqlite:///{os.path.join(basedir, 'instance', 'log.db')}",
        'report':     f"sqlite:///{os.path.join(basedir, 'instance', 'report.db')}",
        'idea':       f"sqlite:///{os.path.join(basedir, 'instance', 'idea.db')}",
        'payroll':    f"sqlite:///{os.path.join(basedir, 'instance', 'payroll.db')}",
        'research':   f"sqlite:///{os.path.join(basedir, 'instance', 'research.db')}",
        'memo':       f"sqlite:///{os.path.join(basedir, 'instance', 'memo.db')}",
        'todo':       f"sqlite:///{os.path.join(basedir, 'instance', 'todo.db')}",
        'budget':     f"sqlite:///{os.path.join(basedir, 'instance', 'budget.db')}",
        'dashboard':  f"sqlite:///{os.path.join(basedir, 'instance', 'dashboard.db')}"
    }

# 本番環境用の設定（今回は変更なし）
class ProductionConfig(Config):
    DEBUG = False
    # ... 本番用の設定を記述 ...

# 設定の呼び出し名を定義
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}