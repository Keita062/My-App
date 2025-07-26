from flask_survey_app.extensions import db
from datetime import datetime

class AnalysisHistory(db.Model):
    """
    分析結果の履歴を保存するためのモデル
    """
    __bind_key__ = 'dashboard'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    analysis_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # 分析結果を直接保存
    preview_html = db.Column(db.Text, nullable=False)
    stats_html = db.Column(db.Text, nullable=False)
    
    # グラフのパスはJSON形式の文字列で保存
    plot_paths_json = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<AnalysisHistory {self.id}: {self.filename}>'