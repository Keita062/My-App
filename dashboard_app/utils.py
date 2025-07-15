import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import io
import base64

def get_data_preview(df):
    """データの先頭50行をHTMLテーブルとして返す"""
    return df.head(50).to_html(classes='data-table', border=0)

def get_basic_stats(df):
    """基本統計量を取得する"""
    stats = df.describe(include='all').transpose()
    # 欠損数を計算して追加
    stats['missing'] = len(df) - stats['count']
    # カラムの順番を調整
    cols_to_show = ['count', 'missing', 'mean', 'std', 'min', '25%', '50%', '75%', 'max', 'unique', 'top', 'freq']
    # 存在するカラムのみ表示
    final_cols = [col for col in cols_to_show if col in stats.columns]
    return stats[final_cols].to_html(classes='data-table', border=0, float_format='{:,.2f}'.format)

def generate_plots(df, plot_dir):
    """データの可視化グラフを生成し、ファイルパスのリストを返す"""
    plot_paths = []
    
    # 数値データのヒストグラムと箱ひげ図を生成
    numeric_cols = df.select_dtypes(include=np.number).columns
    for col in numeric_cols:
        plt.figure(figsize=(8, 6))
        sns.histplot(df[col], kde=True)
        plt.title(f'Histogram of {col}')
        plt.xlabel(col)
        plt.ylabel('Frequency')
        
        img_path = os.path.join(plot_dir, f'hist_{col}.png')
        plt.savefig(img_path)
        plt.close()
        plot_paths.append(f'plots/hist_{col}.png')

    # カテゴリデータの棒グラフを生成 (上位10件)
    category_cols = df.select_dtypes(include=['object', 'category']).columns
    for col in category_cols:
        if df[col].nunique() < 50: # ユニーク数が多すぎる場合はスキップ
            plt.figure(figsize=(10, 7))
            top_10 = df[col].value_counts().nlargest(10)
            sns.barplot(x=top_10.index, y=top_10.values)
            plt.title(f'Top 10 Categories in {col}')
            plt.xlabel(col)
            plt.ylabel('Count')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            
            img_path = os.path.join(plot_dir, f'bar_{col}.png')
            plt.savefig(img_path)
            plt.close()
            plot_paths.append(f'plots/bar_{col}.png')
            
    return plot_paths
