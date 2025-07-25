import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import japanize_matplotlib

def get_data_preview(df):
    """データの先頭50行をHTMLテーブルとして返す"""
    if df is None or df.empty:
        return "<p>データがありません。</p>"
    return df.head(50).to_html(classes='data-table', border=0, justify='left')

def get_basic_stats(df):
    """基本統計量を取得する"""
    if df is None or df.empty:
        return "<p>データがありません。</p>"
    stats = df.describe(include='all').transpose()
    # 欠損数を計算して追加
    stats['欠損数'] = len(df) - stats['count']
    stats.rename(columns={'count': '件数', 'mean': '平均', 'std': '標準偏差', 'min': '最小値', 'max': '最大値', 'unique': 'ユニーク数'}, inplace=True)
    
    # 表示するカラムを定義
    cols_to_show = ['件数', '欠損数', '平均', '標準偏差', '最小値', '25%', '50%', '75%', '最大値', 'ユニーク数', 'top', 'freq']
    # 存在するカラムのみ表示
    final_cols = [col for col in cols_to_show if col in stats.columns]
    return stats[final_cols].to_html(classes='data-table', border=0, float_format='{:,.2f}'.format, justify='left')

def generate_plots(df, plot_dir):
    """データの可視化グラフを生成し、ファイルパスのリストを返す"""
    if df is None or df.empty:
        return []
        
    plot_paths = []
    
    # 数値データのヒストグラムと箱ひげ図を生成
    numeric_cols = df.select_dtypes(include=np.number).columns
    for col in numeric_cols:
        if pd.api.types.is_numeric_dtype(df[col]):
            plt.figure(figsize=(10, 6))
            sns.histplot(df[col].dropna(), kde=True)
            plt.title(f'{col} の分布（ヒストグラム）', fontsize=16)
            plt.xlabel(col, fontsize=12)
            plt.ylabel('度数', fontsize=12)
            plt.grid(axis='y', linestyle='--', alpha=0.7)
            
            img_path = os.path.join(plot_dir, f'hist_{col}.png')
            plt.savefig(img_path)
            plt.close()
            # staticからの相対パスを返す
            plot_paths.append(f'plots/hist_{col}.png')

    # カテゴリデータの棒グラフを生成 (上位20件)
    category_cols = df.select_dtypes(include=['object', 'category']).columns
    for col in category_cols:
        # ユニーク数が多すぎず、少なすぎない場合にグラフ化
        if 1 < df[col].nunique() < 50:
            plt.figure(figsize=(12, 8))
            top_20 = df[col].value_counts().nlargest(20)
            sns.barplot(x=top_20.values, y=top_20.index, orient='h')
            plt.title(f'{col} の内訳（上位20件）', fontsize=16)
            plt.xlabel('件数', fontsize=12)
            plt.ylabel(col, fontsize=12)
            plt.tight_layout() # ラベルがはみ出ないように調整
            
            img_path = os.path.join(plot_dir, f'bar_{col}.png')
            plt.savefig(img_path)
            plt.close()
            # staticからの相対パスを返す
            plot_paths.append(f'plots/bar_{col}.png')
            
    return plot_paths