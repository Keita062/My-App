from flask_sqlalchemy import SQLAlchemy

# SQLAlchemyのインスタンスを作成
# ここでは初期化せず、ファクトリ関数内でappと紐付けます
db = SQLAlchemy()
