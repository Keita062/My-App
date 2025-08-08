from flask import Blueprint, render_template, request, current_app, flash, redirect, url_for
from werkzeug.utils import secure_filename
import os
import pandas as pd
from extensions import db
from .models import AnalysisHistory
from .utils import get_data_preview, get_basic_stats, generate_plots

dashboard_bp = Blueprint('dashboard', 
                         __name__, 
                         template_folder='templates',
                         static_folder='static') # dashboard用のstaticも定義

ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@dashboard_bp.route('/')
def index():
    """アップロードページ兼分析履歴表示"""
    history = AnalysisHistory.query.order_by(AnalysisHistory.analysis_date.desc()).all()
    return render_template('dashboard/index.html', history=history)

@dashboard_bp.route('/upload', methods=['POST'])
def upload_and_analyze():
    """ファイルをアップロードして分析を実行する"""
    if 'file' not in request.files:
        flash('ファイルがリクエストに含まれていません')
        return redirect(url_for('dashboard.index'))
        
    file = request.files['file']

    if file.filename == '':
        flash('ファイルが選択されていません')
        return redirect(url_for('dashboard.index'))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # アップロード先はinstanceフォルダ配下が安全
        upload_folder = os.path.join(current_app.instance_path, 'uploads')
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)

        try:
            df = pd.read_csv(filepath, encoding='utf-8')

            # utils.pyの関数を使って分析データを取得
            preview_html = get_data_preview(df)
            stats_html = get_basic_stats(df)

            # グラフ画像の保存先を定義
            # 注意: プロジェクトルートのstatic/plotsに保存されます
            plot_dir = os.path.join(current_app.root_path, 'static', 'plots')
            if not os.path.exists(plot_dir):
                os.makedirs(plot_dir)
            
            # グラフを生成し、画像パスのリストを取得
            plot_paths = generate_plots(df, plot_dir)

            # 分析履歴をDBに保存
            new_history = AnalysisHistory(
                filename=filename,
                result_summary=f"{len(plot_paths)}個のグラフが生成されました。"
            )
            db.session.add(new_history)
            db.session.commit()
            
            # 分析結果ページにデータを渡して表示
            return render_template('dashboard/analysis.html', 
                                   filename=filename,
                                   preview=preview_html,
                                   stats=stats_html,
                                   plots=plot_paths)
        except Exception as e:
            flash(f'ファイルの処理中にエラーが発生しました: {e}', 'error')
            return redirect(url_for('dashboard.index'))
    else:
        flash('許可されていないファイル形式です。CSVファイルをアップロードしてください。', 'error')
        return redirect(url_for('dashboard.index'))