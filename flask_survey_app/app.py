from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from datetime import datetime
import re
from .extensions import db 

# --- データベースモデル（このファイル内で定義） ---
class Survey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100), nullable=False)
    course_name = db.Column(db.String(100), nullable=True) 
    entry_date = db.Column(db.Date, nullable=False)
    deadline = db.Column(db.Date, nullable=False)
    questions = db.relationship('QuestionAnswer', backref='survey', cascade='all, delete-orphan')

class QuestionAnswer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=True)
    survey_id = db.Column(db.Integer, db.ForeignKey('survey.id'), nullable=False)

# --- Blueprint定義 ---
survey_bp = Blueprint('survey', __name__, template_folder='templates', static_folder='static')

# --- ルーティング ---

@survey_bp.route('/form', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        new_survey = Survey(
            company_name=request.form['company_name'],
            course_name=request.form['course_name'],
            entry_date=datetime.strptime(request.form['entry_date'], '%Y-%m-%d').date(),
            deadline=datetime.strptime(request.form['deadline'], '%Y-%m-%d').date()
        )
        db.session.add(new_survey)
        questions = request.form.getlist('questions[]')
        answers = request.form.getlist('answers[]')
        for q, a in zip(questions, answers):
            if q:
                qa_pair = QuestionAnswer(question=q, answer=a, survey=new_survey)
                db.session.add(qa_pair)
        db.session.commit()
        return redirect(url_for('survey.list_surveys'))
    return render_template('survey/form.html')

@survey_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_survey(id):
    survey = Survey.query.get_or_404(id)
    if request.method == 'POST':
        survey.company_name = request.form['company_name']
        survey.course_name = request.form['course_name']
        survey.entry_date = datetime.strptime(request.form['entry_date'], '%Y-%m-%d').date()
        survey.deadline = datetime.strptime(request.form['deadline'], '%Y-%m-%d').date()
        
        # 既存の質問を一度すべて削除
        for qa in survey.questions:
            db.session.delete(qa)
            
        # フォームの内容で新しい質問を再作成
        questions_text = request.form.getlist('questions[]')
        answers_text = request.form.getlist('answers[]')
        for q, a in zip(questions_text, answers_text):
            if q:
                new_qa = QuestionAnswer(question=q, answer=a, survey=survey)
                db.session.add(new_qa)
        db.session.commit()
        return redirect(url_for('survey.detail_survey', id=id))
    return render_template('survey/edit_survey.html', survey=survey)

@survey_bp.route('/list')
def list_surveys():
    all_surveys = Survey.query.order_by(Survey.deadline.asc()).all()
    return render_template('survey/list.html', surveys=all_surveys)

@survey_bp.route('/survey/<int:id>')
def detail_survey(id):
    survey = Survey.query.get_or_404(id)
    return render_template('survey/detail.html', survey=survey)

@survey_bp.route('/survey/delete/<int:id>', methods=['POST'])
def delete_survey(id):
    survey_to_delete = Survey.query.get_or_404(id)
    db.session.delete(survey_to_delete)
    db.session.commit()
    return redirect(url_for('survey.list_surveys'))
    
@survey_bp.route('/check_company', methods=['POST'])
def check_company():
    data = request.get_json()
    company_name = data.get('company_name')
    if not company_name:
        return jsonify({'exists': False})
    exact_match = Survey.query.filter_by(company_name=company_name).first()
    if not exact_match:
        return jsonify({'exists': False})
    else:
        base_name_escaped = re.escape(company_name)
        pattern = f"^{base_name_escaped}(\\s\\(\\d+\\))?$"
        all_surveys = Survey.query.all()
        similar_surveys = [s for s in all_surveys if re.match(pattern, s.company_name)]
        count = len(similar_surveys)
        suggestion = f"{company_name} ({count + 1})"
        return jsonify({'exists': True, 'suggestion': suggestion})
