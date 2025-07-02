from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)

# ==========================
# DBの初期化（テーブル作成）
# ==========================
def init_db():
    if not os.path.exists('survey.db'):  # DBファイルがないときだけ作る
        conn = sqlite3.connect('survey.db')
        c = conn.cursor()

        # アンケート概要を保存（企業名・締切）
        c.execute('''
            CREATE TABLE survey (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company TEXT,
                deadline TEXT
            )
        ''')

        # 質問と回答テーブル（複数保存する）
        c.execute('''
            CREATE TABLE qa (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                survey_id INTEGER,
                question TEXT,
                answer TEXT,
                FOREIGN KEY(survey_id) REFERENCES survey(id)
            )
        ''')
        conn.commit()
        conn.close()

# ==========================
# ルーティング定義
# ==========================

@app.route('/')
def index():
    return redirect(url_for('form'))  # ルートは /form にリダイレクト

@app.route('/form')
def form():
    return render_template('form.html')  # アンケート入力フォームを表示

@app.route('/submit', methods=['POST'])
def submit():
    # 入力データの取得
    company = request.form.get('company')
    deadline = request.form.get('deadline')
    questions = request.form.getlist('questions[]')  # リスト形式で取得
    answers = request.form.getlist('answers[]')

    # DB保存
    conn = sqlite3.connect('survey.db')
    c = conn.cursor()
    c.execute('INSERT INTO survey (company, deadline) VALUES (?, ?)', (company, deadline))
    survey_id = c.lastrowid  # 直前のIDを取得（外部キー用）

    # 各質問・回答を保存
    for q, a in zip(questions, answers):
        c.execute('INSERT INTO qa (survey_id, question, answer) VALUES (?, ?, ?)', (survey_id, q, a))

    conn.commit()
    conn.close()

    return redirect(url_for('list_surveys'))  # 一覧ページに移動

@app.route('/list')
def list_surveys():
    # 登録済みアンケート一覧を取得
    conn = sqlite3.connect('survey.db')
    c = conn.cursor()
    c.execute('SELECT id, company, deadline FROM survey ORDER BY id DESC')
    surveys = c.fetchall()
    conn.close()
    return render_template('list.html', surveys=surveys)

@app.route('/detail/<int:survey_id>')
def detail(survey_id):
    # アンケート1件分の質問・回答を取得
    conn = sqlite3.connect('survey.db')
    c = conn.cursor()
    c.execute('SELECT company, deadline FROM survey WHERE id=?', (survey_id,))
    survey = c.fetchone()
    c.execute('SELECT question, answer FROM qa WHERE survey_id=?', (survey_id,))
    qa_list = c.fetchall()
    conn.close()
    return render_template('detail.html', survey=survey, qa_list=qa_list)

# ==========================
# 起動時にDB初期化とサーバー起動
# ==========================
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
