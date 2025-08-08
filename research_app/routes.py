from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import db
from .models import Company, SelectionEvent
from datetime import datetime

research_bp = Blueprint('research', __name__, template_folder='templates')

@research_bp.route('/')
def list_companies():
    companies = Company.query.order_by(Company.company_name).all()
    return render_template('research/list.html', companies=companies)

@research_bp.route('/add_company', methods=['GET', 'POST'])
def add_company():
    if request.method == 'POST':
        es_deadline_str = request.form.get('es_deadline')
        es_deadline = datetime.strptime(es_deadline_str, '%Y-%m-%d').date() if es_deadline_str else None
        
        new_company = Company(
            company_name=request.form['company_name'],
            industry=request.form.get('industry'),
            url=request.form.get('url'),
            memo=request.form.get('memo'),
            es_deadline=es_deadline
        )
        db.session.add(new_company)
        db.session.commit()
        flash('企業情報が追加されました。', 'success')
        return redirect(url_for('research.list_companies'))
    return render_template('research/form.html', company=None)

@research_bp.route('/company/<int:id>')
def detail_company(id):
    company = Company.query.get_or_404(id)
    return render_template('research/detail.html', company=company)

@research_bp.route('/edit_company/<int:id>', methods=['GET', 'POST'])
def edit_company(id):
    company = Company.query.get_or_404(id)
    if request.method == 'POST':
        es_deadline_str = request.form.get('es_deadline')
        company.es_deadline = datetime.strptime(es_deadline_str, '%Y-%m-%d').date() if es_deadline_str else None
        
        company.company_name = request.form['company_name']
        company.industry = request.form.get('industry')
        company.url = request.form.get('url')
        company.memo = request.form.get('memo')
        db.session.commit()
        flash('企業情報が更新されました。', 'success')
        return redirect(url_for('research.detail_company', id=id))
    return render_template('research/form.html', company=company)
    
@research_bp.route('/add_event/<int:company_id>', methods=['GET', 'POST'])
def add_event(company_id):
    company = Company.query.get_or_404(company_id)
    if request.method == 'POST':
        event_date_str = request.form.get('event_date')
        event_date = datetime.strptime(event_date_str, '%Y-%m-%dT%H:%M') if event_date_str else None

        if not event_date:
            flash('イベント日時を入力してください。', 'error')
            return render_template('research/event_form.html', company=company)

        new_event = SelectionEvent(
            company_id=company_id,
            event_type=request.form['event_type'],
            event_date=event_date,
            status=request.form['status'],
            notes=request.form.get('notes')
        )
        db.session.add(new_event)
        db.session.commit()
        flash('選考イベントが追加されました。', 'success')
        return redirect(url_for('research.detail_company', id=company_id))
    return render_template('research/event_form.html', company=company)

@research_bp.route('/delete_company/<int:id>', methods=['POST'])
def delete_company(id):
    company = Company.query.get_or_404(id)
    db.session.delete(company)
    db.session.commit()
    flash('企業情報が削除されました。', 'success')
    return redirect(url_for('research.list_companies'))