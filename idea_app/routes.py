from flask import Blueprint, render_template, request, redirect, url_for
from extensions import db
from .models import Idea
from datetime import datetime

idea_bp = Blueprint('idea', __name__, template_folder='templates')

@idea_bp.route('/')
def list_ideas():
    ideas = Idea.query.order_by(Idea.creation_date.desc()).all()
    return render_template('idea/list.html', ideas=ideas)

@idea_bp.route('/add', methods=['GET', 'POST'])
def add_idea():
    if request.method == 'POST':
        due_date_str = request.form.get('due_date')
        due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date() if due_date_str else None
        
        new_idea = Idea(
            category=request.form['category'],
            title=request.form['title'],
            description=request.form['description'],
            due_date=due_date,
            status=request.form['status']
        )
        db.session.add(new_idea)
        db.session.commit()
        return redirect(url_for('idea.list_ideas'))
    return render_template('idea/form.html', idea=None)

@idea_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_idea(id):
    idea = Idea.query.get_or_404(id)
    if request.method == 'POST':
        due_date_str = request.form.get('due_date')
        idea.due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date() if due_date_str else None
        
        idea.category = request.form['category']
        idea.title = request.form['title']
        idea.description = request.form['description']
        idea.status = request.form['status']
        db.session.commit()
        return redirect(url_for('idea.list_ideas'))
    return render_template('idea/form.html', idea=idea)

@idea_bp.route('/delete/<int:id>', methods=['POST'])
def delete_idea(id):
    idea = Idea.query.get_or_404(id)
    db.session.delete(idea)
    db.session.commit()
    return redirect(url_for('idea.list_ideas'))