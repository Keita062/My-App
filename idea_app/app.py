from flask import Blueprint, render_template, request, redirect, url_for
from datetime import datetime
from flask_survey_app.extensions import db
from .models import Idea

idea_bp = Blueprint(
    'idea', 
    __name__,
    template_folder='templates'
)

@idea_bp.route('/')
def list_ideas():
    """アイディアの一覧を表示"""
    # ユーザーがステータスフィルターを明示的に指定したかを確認
    has_status_filter = 'status' in request.args
    
    # クエリパラメータを取得（指定がない場合は空文字''）
    status_filter = request.args.get('status', '')
    category_filter = request.args.get('category', '')

    query = Idea.query

    # --- 【改修点】デフォルト表示のロジック ---
    # フィルターの指定がない場合 (デフォルト表示) は、「完了」ステータスを除外する
    if not has_status_filter:
        query = query.filter(Idea.status != '完了')
    # フィルターが指定されていて、かつ空文字でない（「すべて」でない）場合、そのステータスで絞り込む
    elif status_filter:
        query = query.filter(Idea.status == status_filter)
    # status_filterが空文字''の場合（「すべて」が選択された場合）は、ステータスによる絞り込みは行わない

   
    if category_filter:
        query = query.filter(Idea.category == category_filter)

    # カテゴリのユニークなリストを取得してフィルタ用に渡す
    categories = [c[0] for c in db.session.query(Idea.category).distinct().all() if c[0]]

    all_ideas = query.order_by(Idea.creation_date.desc()).all()
    
    return render_template('idea/list.html', 
                           ideas=all_ideas, 
                           categories=categories,
                           current_status=status_filter,
                           current_category=category_filter)

@idea_bp.route('/new', methods=['GET', 'POST'])
def new_idea():
    """新しいアイディアを作成"""
    if request.method == 'POST':
        due_date_val = None
        if request.form['due_date']:
            due_date_val = datetime.strptime(request.form['due_date'], '%Y-%m-%d').date()

        new_idea = Idea(
            title=request.form['title'],
            details=request.form['details'],
            status=request.form['status'],
            category=request.form['category'],
            priority=request.form['priority'],
            due_date=due_date_val
        )
        db.session.add(new_idea)
        db.session.commit()
        return redirect(url_for('idea.list_ideas'))
    
    return render_template('idea/form.html', idea=None)

@idea_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_idea(id):
    """アイディアを編集"""
    idea = Idea.query.get_or_404(id)
    if request.method == 'POST':
        due_date_val = None
        if request.form['due_date']:
            due_date_val = datetime.strptime(request.form['due_date'], '%Y-%m-%d').date()

        idea.title = request.form['title']
        idea.details = request.form['details']
        idea.status = request.form['status']
        idea.category = request.form['category']
        idea.priority = request.form['priority']
        idea.due_date = due_date_val
        
        db.session.commit()
        return redirect(url_for('idea.list_ideas'))
    
    return render_template('idea/form.html', idea=idea)

@idea_bp.route('/delete/<int:id>', methods=['POST'])
def delete_idea(id):
    """アイディアを削除"""
    idea_to_delete = Idea.query.get_or_404(id)
    db.session.delete(idea_to_delete)
    db.session.commit()
    return redirect(url_for('idea.list_ideas'))