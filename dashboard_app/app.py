import os
from flask import Blueprint, render_template, request, redirect, url_for, current_app, flash
from werkzeug.utils import secure_filename
import pandas as pd
from .utils import get_data_preview, get_basic_stats, generate_plots

dashboard_bp = Blueprint(
    'dashboard', 
    __name__,
    template_folder='templates',
    static_folder='static'
)

# アップロード設定
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
            # アップロードフォルダがなければ作成
            if not os.path.exists(UPLOAD_FOLDER):
                os.makedirs(UPLOAD_FOLDER)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            
            return redirect(url_for('dashboard.analyze', filename=filename))
        else:
            flash('許可されていないファイル形式です (csv, xlsx, xlsのみ)', 'error')
            return redirect(request.url)

    return render_template('dashboard/index.html')

@dashboard_bp.route('/analyze/<filename>')
def analyze(filename):
    """分析結果表示ページ"""
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    
    try:
        if filename.endswith('.csv'):
            df = pd.read_csv(filepath)
        else:
            df = pd.read_excel(filepath)
    except Exception as e:
        flash(f'ファイルの読み込み中にエラーが発生しました: {e}', 'error')
        return redirect(url_for('dashboard.index'))

    # データプレビュー
    preview_html = get_data_preview(df)

    # 基本統計量
    stats_html = get_basic_stats(df)

    # グラフ生成
    plot_dir = os.path.join(current_app.root_path, 'dashboard_app', 'static', 'plots')
    if not os.path.exists(plot_dir):
        os.makedirs(plot_dir)
    plot_paths = generate_plots(df, plot_dir)

    return render_template('dashboard/analysis.html', 
                           filename=filename,
                           preview_html=preview_html,
                           stats_html=stats_html,
                           plot_paths=plot_paths)