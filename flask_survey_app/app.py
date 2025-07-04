from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from datetime import datetime
import re
# 【変更】先頭にドット(.)を追加して、同じフォルダ内のextensionsをインポートするよう修正
from .extensions import db 

# --- データベースモデル（テーブルの設計図）の定義 ---
# モデルの定義は変更なし
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

# --- Blueprintの作成 ---
survey_bp = Blueprint('survey', __name__, template_folder='templates', static_folder='static')


# --- ルーティング（URLと関数の紐付け） ---
@survey_bp.route('/', methods=['GET', 'POST'])
@survey_bp.route('/form', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        company_name = request.form['company_name']
        course_name = request.form['course_name']
        entry_date_str = request.form['entry_date']
        deadline_str = request.form['deadline']

        entry_date = datetime.strptime(entry_date_str, '%Y-%m-%d').date()
        deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date()

        new_survey = Survey(
            company_name=company_name,
            course_name=course_name,
            entry_date=entry_date,
            deadline=deadline
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

from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from datetime import datetime
import re
from .extensions import db 
from .models import Survey, QuestionAnswer # models.pyからインポートするように変更

# (Blueprint定義などは変更なし)
survey_bp = Blueprint('survey', __name__, template_folder='templates', static_folder='static')


# --- 新規登録 ---
@survey_bp.route('/form', methods=['GET', 'POST'])
def form():
    # (変更なし)
    if request.method == 'POST':
        # ( ... 新規登録の処理 ... )
        return redirect(url_for('survey.list_surveys'))
    return render_template('survey/form.html')


# 【新規追加】編集・更新機能
@survey_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_survey(id):
    survey_to_edit = Survey.query.get_or_404(id)

    if request.method == 'POST':
        # --- フォームから送信されたデータでデータベースを更新 ---
        survey_to_edit.company_name = request.form['company_name']
        survey_to_edit.course_name = request.form['course_name']
        survey_to_edit.entry_date = datetime.strptime(request.form['entry_date'], '%Y-%m-%d').date()
        survey_to_edit.deadline = datetime.strptime(request.form['deadline'], '%Y-%m-%d').date()

        # --- 質問と回答の更新 ---
        # フォームから送信された質問ID、質問、回答を取得
        question_ids = request.form.getlist('question_id[]')
        questions_text = request.form.getlist('questions[]')
        answers_text = request.form.getlist('answers[]')

        # 既存の質問を一度すべて削除（簡単のため）
        # より高度な実装ではIDを元に更新・追加・削除を判定します
        for qa in survey_to_edit.questions:
            db.session.delete(qa)
        
        # フォームの内容で新しい質問を再作成
        for q, a in zip(questions_text, answers_text):
            if q: # 質問が空でなければ追加
                new_qa = QuestionAnswer(question=q, answer=a, survey=survey_to_edit)
                db.session.add(new_qa)

        db.session.commit()
        # 更新後は詳細ページにリダイレクト
        return redirect(url_for('survey.detail_survey', id=id))

    # --- GETリクエストの場合：編集フォームを表示 ---
    return render_template('survey/edit_survey.html', survey=survey_to_edit)


# (list_surveys, detail_survey, delete_survey, check_company などの関数は変更なし)
# ...
