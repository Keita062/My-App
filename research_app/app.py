from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime
from sqlalchemy import or_
from flask_survey_app.extensions import db
from .models import Company, SelectionEvent

research_bp = Blueprint(
    'research', 
    __name__,
    template_folder='templates'
)

@research_bp.route('/')
def list_companies():
    """企業の一覧を表示"""
    # フィルタリングと検索、ソートのパラメータを取得
    search_term = request.args.get('search', '')
    industry_filter = request.args.get('industry', '')
    status_filter = request.args.get('status', '')
    sort_by = request.args.get('sort', 'interest')

    query = Company.query

    if search_term:
        query = query.filter(Company.company_name.like(f'%{search_term}%'))
    if industry_filter:
        query = query.filter(Company.industry == industry_filter)
    if status_filter:
        query = query.filter(Company.selection_status == status_filter)

    if sort_by == 'name':
        query = query.order_by(Company.company_name.asc())
    else: # デフォルトは志望度順
        # '高', '中', '低' の順でソート
        query = query.order_by(db.case(
            (Company.interest_level == '高', 1),
            (Company.interest_level == '中', 2),
            (Company.interest_level == '低', 3),
            else_=4
        ))

    companies = query.all()
    
    # フィルタリング用のユニークな業界リストを取得
    industries = [c[0] for c in db.session.query(Company.industry).distinct().all() if c[0]]

    return render_template('research/list.html', 
                           companies=companies, 
                           industries=industries,
                           current_search=search_term,
                           current_industry=industry_filter,
                           current_status=status_filter,
                           current_sort=sort_by)

@research_bp.route('/company/<int:id>')
def detail_company(id):
    """企業詳細ページ"""
    company = Company.query.get_or_404(id)
    return render_template('research/detail.html', company=company)

@research_bp.route('/new', methods=['GET', 'POST'])
def new_company():
    """新規企業登録"""
    if request.method == 'POST':
        # 日付フィールドの変換
        es_deadline = datetime.strptime(request.form['es_deadline'], '%Y-%m-%d').date() if request.form['es_deadline'] else None

        new_company = Company(
            company_name=request.form['company_name'],
            industry=request.form['industry'],
            website_url=request.form['website_url'],
            recruit_url=request.form['recruit_url'],
            business_content=request.form['business_content'],
            philosophy=request.form['philosophy'],
            selection_status=request.form['selection_status'],
            interest_level=request.form['interest_level'],
            applied_position=request.form['applied_position'],
            strength_features=request.form['strength_features'],
            weakness_issues=request.form['weakness_issues'],
            culture=request.form['culture'],
            recent_news=request.form['recent_news'],
            free_memo=request.form['free_memo'],
            es_deadline=es_deadline,
            mypage_id=request.form['mypage_id'],
            mypage_password=request.form['mypage_password']
        )
        db.session.add(new_company)
        db.session.commit()
        flash('新しい企業を登録しました。', 'success')
        return redirect(url_for('research.list_companies'))
    
    return render_template('research/form.html', company=None)

@research_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_company(id):
    """企業情報編集"""
    company = Company.query.get_or_404(id)
    if request.method == 'POST':
        company.company_name = request.form['company_name']
        company.industry = request.form['industry']
        company.website_url = request.form['website_url']
        company.recruit_url = request.form['recruit_url']
        company.business_content = request.form['business_content']
        company.philosophy = request.form['philosophy']
        company.selection_status = request.form['selection_status']
        company.interest_level = request.form['interest_level']
        company.applied_position = request.form['applied_position']
        company.strength_features = request.form['strength_features']
        company.weakness_issues = request.form['weakness_issues']
        company.culture = request.form['culture']
        company.recent_news = request.form['recent_news']
        company.free_memo = request.form['free_memo']
        company.es_deadline = datetime.strptime(request.form['es_deadline'], '%Y-%m-%d').date() if request.form['es_deadline'] else None
        company.mypage_id = request.form['mypage_id']
        company.mypage_password = request.form['mypage_password']
        
        db.session.commit()
        flash('企業情報を更新しました。', 'success')
        return redirect(url_for('research.detail_company', id=id))
        
    return render_template('research/form.html', company=company)

@research_bp.route('/delete/<int:id>', methods=['POST'])
def delete_company(id):
    """企業情報削除"""
    company = Company.query.get_or_404(id)
    db.session.delete(company)
    db.session.commit()
    flash(f'「{company.company_name}」の情報を削除しました。', 'success')
    return redirect(url_for('research.list_companies'))

@research_bp.route('/event/add/<int:company_id>', methods=['POST'])
def add_event(company_id):
    """選考イベントを新規追加"""
    company = Company.query.get_or_404(company_id)
    
    event_date_str = request.form.get('event_date')
    event_date = datetime.strptime(event_date_str, '%Y-%m-%d').date() if event_date_str else datetime.utcnow().date()

    new_event = SelectionEvent(
        event_date=event_date,
        event_type=request.form.get('event_type'),
        memo=request.form.get('memo'),
        company_id=company.id
    )
    db.session.add(new_event)
    db.session.commit()
    flash('新しい選考イベントを記録しました。', 'success')
    return redirect(url_for('research.detail_company', id=company_id))

@research_bp.route('/event/edit/<int:event_id>', methods=['GET', 'POST'])
def edit_event(event_id):
    """選考イベントを編集"""
    event = SelectionEvent.query.get_or_404(event_id)
    if request.method == 'POST':
        event.event_date = datetime.strptime(request.form['event_date'], '%Y-%m-%d').date()
        event.event_type = request.form['event_type']
        event.memo = request.form['memo']
        db.session.commit()
        flash('選考イベントを更新しました。', 'success')
        return redirect(url_for('research.detail_company', id=event.company_id))
    
    return render_template('research/event_form.html', event=event)

@research_bp.route('/event/delete/<int:event_id>', methods=['POST'])
def delete_event(event_id):
    """選考イベントを削除"""
    event = SelectionEvent.query.get_or_404(event_id)
    company_id = event.company_id
    db.session.delete(event)
    db.session.commit()
    flash('選考イベントを削除しました。', 'success')
    return redirect(url_for('research.detail_company', id=company_id))