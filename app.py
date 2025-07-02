import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# --- アプリケーションとデータベースの初期設定 ---
# ベースディレクトリの絶対パスを取得
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
# SQLAlchemyの設定
# データベースファイルの保存場所を指定
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'survey.db')
# SQLAlchemyのイベントシステムを無効にし、オーバーヘッドを削減
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# SQLAlchemyのインスタンスを作成
db = SQLAlchemy(app)

# --- データベースモデル（テーブルの設計図）の定義 ---

# Surveyモデル: 企業名と締切日を保存
class Survey(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # 主キー
    company_name = db.Column(db.String(100), nullable=False) # 企業名（空であってはならない）
    deadline = db.Column(db.Date, nullable=False) # 締切日（空であってはならない）
    
    # SurveyからQuestionAnswerへのリレーションシップを定義
    # 'backref'はQuestionAnswerからSurveyを逆参照できるようにする
    # 'cascade'はSurveyが削除されたときに関連するQuestionAnswerも削除する設定
    questions = db.relationship('QuestionAnswer', backref='survey', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Survey {self.company_name}>'

# QuestionAnswerモデル: 質問と回答のペアを保存
class QuestionAnswer(db.Model):
    id = db.Column(db.Integer, primary_key=True) # 主キー
    question = db.Column(db.Text, nullable=False) # 質問内容
    answer = db.Column(db.Text, nullable=True)   # 回答内容（任意）
    
    # 外部キー: Surveyテーブルのidと紐付ける
    survey_id = db.Column(db.Integer, db.ForeignKey('survey.id'), nullable=False)

    def __repr__(self):
        return f'<Question {self.question[:20]}>'


# --- ルーティング（URLと関数の紐付け） ---

# ルートURL ('/') および '/form' へのアクセス
@app.route('/', methods=['GET', 'POST'])
@app.route('/form', methods=['GET', 'POST'])
def form():
    # POSTリクエスト（フォームが送信された）の場合
    if request.method == 'POST':
        # フォームからデータを取得
        company_name = request.form['company_name']
        # 文字列の日付をdatetime.dateオブジェクトに変換
        deadline_str = request.form['deadline']
        deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date()

        # 新しいSurveyオブジェクトを作成してデータベースセッションに追加
        new_survey = Survey(company_name=company_name, deadline=deadline)
        db.session.add(new_survey)

        # 質問と回答のペアを取得
        questions = request.form.getlist('questions[]')
        answers = request.form.getlist('answers[]')

        # 各ペアをQuestionAnswerオブジェクトとして作成し、Surveyに紐付ける
        for q, a in zip(questions, answers):
            if q: # 質問が空でなければ
                qa_pair = QuestionAnswer(question=q, answer=a, survey=new_survey)
                db.session.add(qa_pair)
        
        # データベースに変更をコミット（保存）
        db.session.commit()
        
        # 保存後、一覧ページにリダイレクト
        return redirect(url_for('list_surveys'))
    
    # GETリクエスト（ページを最初に表示する）の場合
    return render_template('form.html')

# '/list' へのアクセス
@app.route('/list')
def list_surveys():
    # すべてのSurveyデータを締切日の昇順で取得
    all_surveys = Survey.query.order_by(Survey.deadline.asc()).all()
    # 取得したデータをテンプレートに渡して表示
    return render_template('list.html', surveys=all_surveys)

# '/survey/<id>' へのアクセス（特定のアンケート詳細）
@app.route('/survey/<int:id>')
def detail_survey(id):
    # 指定されたIDのSurveyデータを取得（見つからなければ404エラー）
    survey = Survey.query.get_or_404(id)
    # 取得したデータをテンプレートに渡して表示
    return render_template('detail.html', survey=survey)

# '/survey/delete/<id>' へのアクセス（アンケート削除）
@app.route('/survey/delete/<int:id>', methods=['POST'])
def delete_survey(id):
    # 削除対象のSurveyデータを取得
    survey_to_delete = Survey.query.get_or_404(id)
    # データベースセッションから削除
    db.session.delete(survey_to_delete)
    # 変更をコミット
    db.session.commit()
    # 一覧ページにリダイレクト
    return redirect(url_for('list_surveys'))


# --- アプリケーションの実行 ---
if __name__ == '__main__':
    # アプリケーションコンテキスト内でデータベースを作成
    with app.app_context():
        db.create_all()
    # デバッグモードでアプリケーションを起動
    app.run(debug=True)
