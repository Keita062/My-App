from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime
from extensions import db  # 変更点：共通のextensions.pyからdbをインポート
from .models import Todo

todo_bp = Blueprint(
    'todo', 
    __name__,
    template_folder='templates',
    static_folder='static'
)

# ↓↓↓↓↓↓  これ以下のルート定義のコードは、元のapp.pyから一切変更ありません ↓↓↓↓↓↓

@todo_bp.route('/')
def list_tasks():
    """ToDoリストのメインページを表示"""
    tasks = Todo.query.order_by(Todo.created_at.desc()).all()
    return render_template('todo/list.html', tasks=tasks)

@todo_bp.route('/add', methods=['POST'])
def add_task():
    """新しいタスクを追加"""
    content = request.form.get('content')
    due_date_str = request.form.get('due_date')

    if not content:
        flash('タスク内容を入力してください。', 'error')
        return redirect(url_for('todo.list_tasks'))

    due_date = datetime.strptime(due_date_str, '%Y-%m-%dT%H:%M') if due_date_str else None
    
    new_task = Todo(content=content, due_date=due_date)
    db.session.add(new_task)
    db.session.commit()
    
    flash('新しいタスクを追加しました。', 'success')
    return redirect(url_for('todo.list_tasks'))

@todo_bp.route('/toggle/<int:id>', methods=['POST'])
def toggle_task(id):
    """タスクの完了/未完了を切り替える"""
    task = Todo.query.get_or_404(id)
    task.completed = not task.completed
    db.session.commit()
    return jsonify({'success': True, 'completed': task.completed})

@todo_bp.route('/delete/<int:id>', methods=['POST'])
def delete_task(id):
    """タスクを削除する"""
    task = Todo.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()
    return jsonify({'success': True})

@todo_bp.route('/update/<int:id>', methods=['POST'])
def update_task(id):
    """タスクの内容と期日を更新する"""
    task = Todo.query.get_or_404(id)
    content = request.form.get('content')
    due_date_str = request.form.get('due_date')
    
    if not content:
        return jsonify({'success': False, 'error': '内容は必須です。'})

    task.content = content
    task.due_date = datetime.strptime(due_date_str, '%Y-%m-%dT%H:%M') if due_date_str else None
    
    db.session.commit()
    return jsonify({'success': True})