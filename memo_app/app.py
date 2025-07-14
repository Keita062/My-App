from flask import Blueprint, render_template, request, redirect, url_for, flash
from sqlalchemy import or_
import markdown2
from flask_survey_app.extensions import db
from .models import Memo

memo_bp = Blueprint(
    'memo', 
    __name__,
    template_folder='templates'
)

@memo_bp.route('/')
def list_memos():
    """メモの一覧を表示"""
    search_term = request.args.get('search', '')
    
    query = Memo.query
    if search_term:
        query = query.filter(or_(
            Memo.title.like(f'%{search_term}%'),
            Memo.content.like(f'%{search_term}%'),
            Memo.tags.like(f'%{search_term}%')
        ))

    # ピン留めされたものを先に、次に更新日の新しい順でソート
    memos = query.order_by(Memo.is_pinned.desc(), Memo.updated_at.desc()).all()

    # MarkdownをHTMLに変換してプレビュー用に渡す
    for memo in memos:
        if memo.content:
            # 最初の100文字だけプレビュー
            snippet = memo.content[:100]
            memo.content_html = markdown2.markdown(snippet, extras=["fenced-code-blocks", "tables"])
        else:
            memo.content_html = ""

    return render_template('memo/list.html', memos=memos, search_term=search_term)

@memo_bp.route('/new', methods=['GET', 'POST'])
def new_memo():
    """新しいメモを作成"""
    if request.method == 'POST':
        new_memo = Memo(
            title=request.form['title'],
            content=request.form['content'],
            tags=request.form['tags']
        )
        db.session.add(new_memo)
        db.session.commit()
        flash('メモが作成されました。', 'success')
        return redirect(url_for('memo.list_memos'))
    
    return render_template('memo/form.html', memo=None)

@memo_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_memo(id):
    """メモを編集"""
    memo = Memo.query.get_or_404(id)
    if request.method == 'POST':
        memo.title = request.form['title']
        memo.content = request.form['content']
        memo.tags = request.form['tags']
        db.session.commit()
        flash('メモが更新されました。', 'success')
        return redirect(url_for('memo.list_memos'))
    
    if memo.content:
        memo.content_html = markdown2.markdown(memo.content, extras=["fenced-code-blocks", "tables"])
    else:
        memo.content_html = ""

    return render_template('memo/form.html', memo=memo)

@memo_bp.route('/delete/<int:id>', methods=['POST'])
def delete_memo(id):
    """メモを削除"""
    memo = Memo.query.get_or_404(id)
    db.session.delete(memo)
    db.session.commit()
    flash('メモが削除されました。', 'success')
    return redirect(url_for('memo.list_memos'))

@memo_bp.route('/pin/<int:id>', methods=['POST'])
def toggle_pin(id):
    """メモのピン留め状態を切り替える"""
    memo = Memo.query.get_or_404(id)
    memo.is_pinned = not memo.is_pinned
    db.session.commit()
    return redirect(url_for('memo.list_memos'))
