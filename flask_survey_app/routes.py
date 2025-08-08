from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import db
from .models import Survey  # 新しく作成したmodels.pyからSurveyモデルをインポート
from datetime import datetime

# 'survey'という名前でBlueprintを作成
survey_bp = Blueprint('survey', 
                      __name__, 
                      template_folder='templates', 
                      static_folder='static')

@survey_bp.route('/')
def list_surveys():
    """ESの一覧を表示する"""
    surveys = Survey.query.all()
    return render_template('survey/list.html', surveys=surveys)

@survey_bp.route('/new', methods=['GET', 'POST'])
def add_survey():
    """新しいESを登録する"""
    if request.method == 'POST':
        # フォームから送信されたデータを取得
        company_name = request.form.get('company_name')
        deadline_str = request.form.get('deadline')
        questions = request.form.get('questions')
        answers = request.form.get('answers')
        status = request.form.get('status')
        evaluation = request.form.get('evaluation')
        memo = request.form.get('memo')

        # 日付文字列をdatetimeオブジェクトに変換
        deadline = datetime.strptime(deadline_str, '%Y-%m-%dT%H:%M') if deadline_str else None

        # 新しいSurveyオブジェクトを作成
        new_survey = Survey(
            company_name=company_name,
            deadline=deadline,
            questions=questions,
            answers=answers,
            status=status,
            evaluation=evaluation,
            memo=memo
        )

        # データベースに追加して保存
        db.session.add(new_survey)
        db.session.commit()

        flash('新しいESが登録されました。')
        return redirect(url_for('survey.list_surveys'))
    
    # GETリクエストの場合は登録フォームを表示
    return render_template('survey/form.html')

@survey_bp.route('/<int:id>')
def detail_survey(id):
    """ESの詳細を表示する"""
    survey = Survey.query.get_or_404(id)
    return render_template('survey/detail.html', survey=survey)

@survey_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_survey(id):
    """既存のESを編集する"""
    survey = Survey.query.get_or_404(id)
    if request.method == 'POST':
        # フォームから送信されたデータでsurveyオブジェクトを更新
        survey.company_name = request.form.get('company_name')
        deadline_str = request.form.get('deadline')
        survey.deadline = datetime.strptime(deadline_str, '%Y-%m-%dT%H:%M') if deadline_str else None
        survey.questions = request.form.get('questions')
        survey.answers = request.form.get('answers')
        survey.status = request.form.get('status')
        survey.evaluation = request.form.get('evaluation')
        survey.memo = request.form.get('memo')

        # データベースの変更を保存
        db.session.commit()
        
        flash('ESが更新されました。')
        return redirect(url_for('survey.detail_survey', id=survey.id))
    
    # GETリクエストの場合は編集フォームを表示
    return render_template('survey/edit_survey.html', survey=survey)

@survey_bp.route('/delete/<int:id>', methods=['POST'])
def delete_survey(id):
    """ESを削除する"""
    survey = Survey.query.get_or_404(id)
    db.session.delete(survey)
    db.session.commit()
    flash('ESが削除されました。')
    return redirect(url_for('survey.list_surveys'))