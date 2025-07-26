from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime
import json
from flask_survey_app.extensions import db
from .models import Client, Budget

budget_bp = Blueprint(
    'budget', 
    __name__,
    template_folder='templates',
    static_folder='static'
)

@budget_bp.route('/')
def index():
    """予算調整ツールのメインページ"""
    clients = Client.query.order_by(Client.name).all()
    return render_template('budget/calculator.html', clients=clients)

@budget_bp.route('/calculate', methods=['POST'])
def calculate():
    """AJAXリクエストを受け取り、予算を計算してJSONで返す"""
    try:
        data = request.get_json()
        
        gross_amount = float(data.get('gross_amount', 0))
        calc_method = data.get('calculation_method', '内掛け')
        broadcast_amount = float(data.get('broadcast_amount', 0))
        client_id = data.get('client_id')
        creatives = data.get('creatives', [])
        
        client = Client.query.get(client_id)
        if not client:
            return jsonify({'error': 'クライアントが見つかりません'}), 400
            
        commission_rate = client.commission_rate / 100.0

        # ネット金額の計算
        if calc_method == '内掛け':
            net_amount = gross_amount * (1 - commission_rate)
        else: # 外掛け
            net_amount = gross_amount / (1 + commission_rate)
        
        usable_amount = net_amount - broadcast_amount

        # 着地見込みなどの計算
        total_days_in_month = 31 # 仮。実際にはJS側で当月の日数を計算
        if 'total_days' in data:
            total_days_in_month = int(data['total_days'])
        
        elapsed_days = int(data.get('elapsed_days', 1))
        remaining_days = total_days_in_month - elapsed_days

        results = []
        for creative in creatives:
            budget = float(creative.get('budget', 0))
            actuals = float(creative.get('actuals', 0))
            
            daily_budget_future = (budget - actuals) / remaining_days if remaining_days > 0 else 0
            projected_landing = actuals + (daily_budget_future * remaining_days)
            
            results.append({
                'name': creative.get('name', 'N/A'),
                'budget': budget,
                'actuals': actuals,
                'daily_budget_future': daily_budget_future,
                'projected_landing': projected_landing
            })

        return jsonify({
            'net_amount': net_amount,
            'usable_amount': usable_amount,
            'creative_results': results
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@budget_bp.route('/clients')
def list_clients():
    """クライアント一覧ページ"""
    clients = Client.query.order_by(Client.name).all()
    return render_template('budget/client_list.html', clients=clients)

@budget_bp.route('/client/add', methods=['POST'])
def add_client():
    """新しいクライアントを追加"""
    name = request.form.get('name')
    rate = request.form.get('commission_rate')
    if name and rate:
        if Client.query.filter_by(name=name).first():
            flash(f'クライアント「{name}」は既に存在します。', 'error')
        else:
            new_client = Client(name=name, commission_rate=float(rate))
            db.session.add(new_client)
            db.session.commit()
            flash('新しいクライアントを追加しました。', 'success')
    else:
        flash('クライアント名と手数料率を入力してください。', 'error')
    return redirect(url_for('budget.list_clients'))

@budget_bp.route('/client/edit/<int:id>', methods=['POST'])
def edit_client(id):
    """クライアント情報を更新"""
    client = Client.query.get_or_404(id)
    name = request.form.get('name')
    rate = request.form.get('commission_rate')
    if name and rate:
        client.name = name
        client.commission_rate = float(rate)
        db.session.commit()
        flash('クライアント情報を更新しました。', 'success')
    else:
        flash('クライアント名と手数料率を入力してください。', 'error')
    return redirect(url_for('budget.list_clients'))

@budget_bp.route('/client/delete/<int:id>', methods=['POST'])
def delete_client(id):
    """クライアントを削除"""
    client = Client.query.get_or_404(id)
    db.session.delete(client)
    db.session.commit()
    flash('クライアントを削除しました。', 'success')
    return redirect(url_for('budget.list_clients'))