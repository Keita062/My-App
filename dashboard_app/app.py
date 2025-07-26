import os
import logging
import json
from logging.handlers import RotatingFileHandler
from flask import Blueprint, render_template, request, redirect, url_for, current_app, flash
from werkzeug.utils import secure_filename
import pandas as pd
from .utils import get_data_preview, get_basic_stats, generate_plots
from flask_survey_app.extensions import db
from .models import AnalysisHistory

dashboard_bp = Blueprint(
    'dashboard', 
    __name__,
    # 【修正】template_folderの指定を削除し、より標準的な設定に変更
    template_folder='templates',
    static_folder='static'
)

# --- ロギング設定 ---
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)
logger = logging.getLogger(f'dashboard_app.{__name__}')
logger.setLevel(logging.ERROR)
handler = RotatingFileHandler(
    os.path.join(LOG_DIR, 'errors.log'), 
    maxBytes=1024 * 1024,
    backupCount=3,
    encoding='utf-8'
)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s [in %(pathname)s:%(lineno)d]')
handler.setFormatter(formatter)
if not logger.handlers:
    logger.addHandler(handler)

# --- アップロード設定 ---
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@dashboard_bp.route('/', methods=['GET', 'POST'])
def index():
    """ファイルアップロードページ & 履歴一覧"""
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('ファイルが選択されていません', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('ファイルが選択されていません', 'error')
            return redirect(request.url)
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            if not os.path.exists(UPLOAD_FOLDER):
                os.makedirs(UPLOAD_FOLDER)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            
            # --- 分析と履歴保存 ---
            try:
                if filename.lower().endswith('.csv'):
                    try:
                        df = pd.read_csv(filepath, encoding='utf-8-sig')
                    except UnicodeDecodeError:
                        df = pd.read_csv(filepath, encoding='shift-jis')
                else:
                    df = pd.read_excel(filepath)

                preview_html = get_data_preview(df)
                stats_html = get_basic_stats(df)
                plot_dir = os.path.join(current_app.static_folder, 'plots')
                if not os.path.exists(plot_dir):
                    os.makedirs(plot_dir)
                plot_paths = generate_plots(df, plot_dir)

                # 履歴をDBに保存
                new_history = AnalysisHistory(
                    filename=filename,
                    preview_html=preview_html,
                    stats_html=stats_html,
                    plot_paths_json=json.dumps(plot_paths)
                )
                db.session.add(new_history)
                db.session.commit()
                
                flash('分析が完了し、履歴に保存されました。', 'success')
                return redirect(url_for('dashboard.view_history', id=new_history.id))

            except Exception as e:
                logger.error(f"Error analyzing file '{filename}': {e}", exc_info=True)
                flash(f'ファイルの分析中にエラーが発生しました。詳細はログを確認してください。', 'error')
                return redirect(request.url)
        else:
            flash('許可されていないファイル形式です (csv, xlsx, xlsのみ)', 'error')
            return redirect(request.url)

    # GETリクエストの場合、履歴一覧を表示
    histories = AnalysisHistory.query.order_by(AnalysisHistory.analysis_date.desc()).all()
    # 【修正】テンプレートのパスを 'dashboard/index.html' に変更
    return render_template('dashboard/index.html', histories=histories)

@dashboard_bp.route('/history/<int:id>')
def view_history(id):
    """保存された分析結果を表示"""
    history = AnalysisHistory.query.get_or_404(id)
    plot_paths = json.loads(history.plot_paths_json)
    # 【修正】テンプレートのパスを 'dashboard/analysis.html' に変更
    return render_template('dashboard/analysis.html', history=history, plot_paths=plot_paths)

@dashboard_bp.route('/history/delete/<int:id>', methods=['POST'])
def delete_history(id):
    """分析履歴を削除"""
    history = AnalysisHistory.query.get_or_404(id)
    db.session.delete(history)
    db.session.commit()
    flash('分析履歴を削除しました。', 'success')
    return redirect(url_for('dashboard.index'))