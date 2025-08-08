from flask import Blueprint, render_template, request, redirect, url_for
from extensions import db
from .models import Memo

memo_bp = Blueprint('memo', __name__, template_folder='templates')

@memo_bp.route('/')
def list_memos():
    memos = Memo.query.order_by(Memo.created_at.desc()).all()
    return render_template('memo/list.html', memos=memos)

@memo_bp.route('/add', methods=['POST'])
def add_memo():
    content = request.form.get('content')
    if content:
        new_memo = Memo(content=content)
        db.session.add(new_memo)
        db.session.commit()
    return redirect(url_for('memo.list_memos'))

@memo_bp.route('/edit/<int:id>', methods=['POST'])
def edit_memo(id):
    memo = Memo.query.get_or_404(id)
    memo.content = request.form.get('content')
    db.session.commit()
    return redirect(url_for('memo.list_memos'))

@memo_bp.route('/delete/<int:id>', methods=['POST'])
def delete_memo(id):
    memo = Memo.query.get_or_404(id)
    db.session.delete(memo)
    db.session.commit()
    return redirect(url_for('memo.list_memos'))