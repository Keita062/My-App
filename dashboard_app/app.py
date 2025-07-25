import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Blueprint, render_template, request, redirect, url_for, current_app, flash
from werkzeug.utils import secure_filename
import pandas as pd
from .utils import get_data_preview, get_basic_stats, generate_plots

dashboard_bp = Blueprint(
    'dashboard', 
    __name__,
    template_folder='templates/dashboard', # テンプレートフォルダを正しく指定
    static_folder='static'
)

# --- ロギング設定 ---
# ログファイルの保存先ディレクトリ
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# ロガーのセットアップ
logger = logging.getLogger(f'dashboard_app.{__name__}')
logger.setLevel(logging.ERROR)
handler = RotatingFileHandler(
    os.path.join(LOG_DIR, 'errors.log'), 
    maxBytes=1024 * 1024, # 1MB
    backupCount=3,
    encoding='utf-8' # 文字コードを指定
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
    """ファイルアップロードページ"""
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
            
            return redirect(url_for('dashboard.analyze', filename=filename))
        else:
            flash('許可されていないファイル形式です (csv, xlsx, xlsのみ)', 'error')
            return redirect(request.url)

    # 修正: index.htmlのパスを修正
    return render_template('index.html')

@dashboard_bp.route('/analyze/<filename>')
def analyze(filename):
    """分析結果表示ページ"""
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    
    try:
        if not os.path.exists(filepath):
            flash('ファイルが見つかりません。再度アップロードしてください。', 'error')
            logger.error(f"File not found: {filepath}")
            return redirect(url_for('dashboard.index'))

        if filename.lower().endswith('.csv'):
            # BOM付きUTF-8に対応するため 'utf-8-sig' を試す
            try:
                df = pd.read_csv(filepath, encoding='utf-8-sig')
            except UnicodeDecodeError:
                df = pd.read_csv(filepath, encoding='shift-jis') # Shift-JISも試す
        else:
            df = pd.read_excel(filepath)

    except Exception as e:
        # エラーをログに記録
        logger.error(f"Error reading file '{filename}': {e}", exc_info=True)
        flash(f'ファイルの読み込み中にエラーが発生しました。詳細はログを確認してください。', 'error')
        return redirect(url_for('dashboard.index'))

    # データプレビュー
    preview_html = get_data_preview(df)

    # 基本統計量
    stats_html = get_basic_stats(df)

    # グラフ生成
    plot_dir = os.path.join(current_app.static_folder, 'plots') # staticフォルダを直接参照
    if not os.path.exists(plot_dir):
        os.makedirs(plot_dir)
    plot_paths = generate_plots(df, plot_dir)

    # 修正: analysis.htmlのパスを修正
    return render_template('analysis.html', 
                           filename=filename,
                           preview_html=preview_html,
                           stats_html=stats_html,
                           plot_paths=plot_paths)