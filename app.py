import os
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import re

# --- アプリケーションとデータベースの初期設定 ---
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'survey.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- データベースモデル（テーブルの設計図）の定義 ---

class Survey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100), nullable=False)
    # 【追加】コース名
    course_name = db.Column(db.String(100), nullable=True) 
    # 【追加】打ち込み日
    entry_date = db.Column(db.Date, nullable=False)
    deadline = db.Column(db.Date, nullable=False)
    
    questions = db.relationship('QuestionAnswer', backref='survey', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Survey {self.company_name}>'

class QuestionAnswer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=True)
    survey_id = db.Column(db.Integer, db.ForeignKey('survey.id'), nullable=False)

    def __repr__(self):
        return f'<Question {self.question[:20]}>'


# --- ルーティング（URLと関数の紐付け） ---

@app.route('/', methods=['GET', 'POST'])
@app.route('/form', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        # フォームからデータを取得
        company_name = request.form['company_name']
        course_name = request.form['course_name']
        entry_date_str = request.form['entry_date']
        deadline_str = request.form['deadline']

        # 文字列を日付オブジェクトに変換
        entry_date = datetime.strptime(entry_date_str, '%Y-%m-%d').date()
        deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date()

        # 新しいSurveyオブジェクトを作成
        new_survey = Survey(
            company_name=company_name,
            course_name=course_name,
            entry_date=entry_date,
            deadline=deadline
        )
        db.session.add(new_survey)

        # 質問と回答のペアを取得
        questions = request.form.getlist('questions[]')
        answers = request.form.getlist('answers[]')

        for q, a in zip(questions, answers):
            if q:
                qa_pair = QuestionAnswer(question=q, answer=a, survey=new_survey)
                db.session.add(qa_pair)
        
        db.session.commit()
        return redirect(url_for('list_surveys'))
    
    return render_template('form.html')

# 【新規追加】企業名の重複をチェックするためのAPIエンドポイント
@app.route('/check_company', methods=['POST'])
def check_company():
    data = request.get_json()
    company_name = data.get('company_name')
    if not company_name:
        return jsonify({'exists': False})

    # 完全一致する企業名を検索
    exact_match = Survey.query.filter_by(company_name=company_name).first()
    
    if not exact_match:
        # 重複がない場合
        return jsonify({'exists': False})
    else:
        # 重複がある場合、類似の企業名（例: "企業名 (2)"）をすべて検索
        base_name_escaped = re.escape(company_name)
        # "企業名" または "企業名 (数字)" のパターンに一致するものを検索
        pattern = f"^{base_name_escaped}(\s\(\d+\))?$"
        
        all_surveys = Survey.query.all()
        similar_surveys = [s for s in all_surveys if re.match(pattern, s.company_name)]
        
        count = len(similar_surveys)
        suggestion = f"{company_name} ({count + 1})"
        return jsonify({'exists': True, 'suggestion': suggestion})


@app.route('/list')
def list_surveys():
    all_surveys = Survey.query.order_by(Survey.deadline.asc()).all()
    return render_template('list.html', surveys=all_surveys)

@app.route('/survey/<int:id>')
def detail_survey(id):
    survey = Survey.query.get_or_404(id)
    return render_template('detail.html', survey=survey)

@app.route('/survey/delete/<int:id>', methods=['POST'])
def delete_survey(id):
    survey_to_delete = Survey.query.get_or_404(id)
    db.session.delete(survey_to_delete)
    db.session.commit()
    return redirect(url_for('list_surveys'))


# --- アプリケーションの実行 ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
