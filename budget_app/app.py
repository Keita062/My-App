from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime
import json
from flask_survey_app.extensions import db
from .models import Client, BudgetSimulation
from sqlalchemy import desc

budget_bp = Blueprint(
    'budget', 
    __name__,
    # 【修正】テンプレートフォルダのパスを正しく指定
    template_folder='templates/budget'
)

@budget_bp.route('/')
def list_simulations():
    """保存されたシミュレーションの一覧を表示"""
    simulations = BudgetSimulation.query.order_by(desc(BudgetSimulation.simulation_date)).all()
    # 【修正】テンプレートのパスを修正
    return render_template('list.html', simulations=simulations)

@budget_bp.route('/new', methods=['GET'])
def new_simulation():
    """新規シミュレーション作成ページ"""
    clients = Client.query.order_by(Client.name).all()
    last_simulation = BudgetSimulation.query.order_by(desc(BudgetSimulation.created_at)).first()
    today = datetime.utcnow().date()
    # 【修正】テンプレートのパスを修正
    return render_template('form.html', clients=clients, simulation=None, last_simulation=last_simulation, today=today)

@budget_bp.route('/edit/<int:id>', methods=['GET'])
def edit_simulation(id):
    """シミュレーション編集ページ"""
    simulation = BudgetSimulation.query.get_or_404(id)
    clients = Client.query.order_by(Client.name).all()
    today = datetime.utcnow().date()
    # 【修正】テンプレートのパスを修正
    return render_template('form.html', clients=clients, simulation=simulation, last_simulation=None, today=today)

@budget_bp.route('/save', methods=['POST'])
def save_simulation():
    """シミュレーションを保存（新規・更新）"""
    form_data = request.form
    
    try:
        sim_id = form_data.get('simulation_id')
        
        creatives = []
        creative_names = form_data.getlist('creative_name[]')
        creative_actuals = form_data.getlist('creative_actuals[]')
        creative_percentages = form_data.getlist('creative_percentage[]')
        
        for i in range(len(creative_names)):
            creatives.append({
                "name": creative_names[i],
                "actuals": float(creative_actuals[i] or 0),
                "percentage": float(creative_percentages[i] or 0)
            })

        if sim_id: # 更新
            sim = BudgetSimulation.query.get_or_404(sim_id)
            sim.title = form_data['title']
            sim.simulation_date = datetime.strptime(form_data['simulation_date'], '%Y-%m-%d').date()
            sim.target_year = int(form_data['target_year'])
            sim.target_month = int(form_data['target_month'])
            sim.gross_amount = float(form_data['gross_amount'])
            sim.calculation_method = form_data['calculation_method']
            sim.commission_rate_used = float(form_data['commission_rate_used'])
            sim.broadcast_amount = float(form_data['broadcast_amount'])
            sim.remaining_days = int(form_data['remaining_days'])
            sim.client_id = form_data['client_id']
            sim.simulation_details = json.dumps(creatives, ensure_ascii=False)
            flash('シミュレーションを更新しました。', 'success')
        else: # 新規作成
            new_sim = BudgetSimulation(
                title=form_data['title'],
                simulation_date=datetime.strptime(form_data['simulation_date'], '%Y-%m-%d').date(),
                target_year=int(form_data['target_year']),
                target_month=int(form_data['target_month']),
                gross_amount=float(form_data['gross_amount']),
                calculation_method=form_data['calculation_method'],
                commission_rate_used=float(form_data['commission_rate_used']),
                broadcast_amount=float(form_data['broadcast_amount']),
                remaining_days=int(form_data['remaining_days']),
                client_id=form_data['client_id'],
                simulation_details=json.dumps(creatives, ensure_ascii=False)
            )
            db.session.add(new_sim)
            flash('シミュレーションを保存しました。', 'success')
            
        db.session.commit()

    except Exception as e:
        flash(f'保存中にエラーが発生しました: {e}', 'error')

    return redirect(url_for('budget.list_simulations'))

@budget_bp.route('/delete/<int:id>', methods=['POST'])
def delete_simulation(id):
    """シミュレーションを削除"""
    sim = BudgetSimulation.query.get_or_404(id)
    db.session.delete(sim)
    db.session.commit()
    flash('シミュレーションを削除しました。', 'success')
    return redirect(url_for('budget.list_simulations'))

@budget_bp.route('/compare', methods=['GET'])
def compare_simulations():
    """2つのシミュレーションを比較"""
    sim_id_a = request.args.get('sim_a', type=int)
    sim_id_b = request.args.get('sim_b', type=int)

    if not sim_id_a or not sim_id_b:
        flash('比較するシミュレーションを2つ選択してください。', 'error')
        return redirect(url_for('budget.list_simulations'))
        
    sim_a = BudgetSimulation.query.get_or_404(sim_id_a)
    sim_b = BudgetSimulation.query.get_or_404(sim_id_b)

    data_a = calculate_full_simulation(sim_a)
    data_b = calculate_full_simulation(sim_b)
    
    comparison_data = generate_comparison(data_a, data_b)

    return render_template('compare.html', sim_a=sim_a, sim_b=sim_b, comparison=comparison_data)

def calculate_full_simulation(sim):
    """シミュレーションオブジェクトから全ての計算結果を算出するヘルパー関数"""
    details = json.loads(sim.simulation_details)
    
    if sim.calculation_method == '内掛け':
        net_amount = sim.gross_amount * (1 - (sim.commission_rate_used / 100.0))
    else:
        net_amount = sim.gross_amount / (1 + (sim.commission_rate_used / 100.0))
    
    usable_amount = net_amount - sim.broadcast_amount
    
    total_actuals = sum(c.get('actuals', 0) for c in details)
    future_total_usable = usable_amount - total_actuals
    
    creative_results = []
    for creative in details:
        percentage = creative.get('percentage', 0)
        actuals = creative.get('actuals', 0)
        
        future_budget = future_total_usable * (percentage / 100.0)
        daily_budget = future_budget / sim.remaining_days if sim.remaining_days > 0 else 0
        projected_landing = actuals + future_budget
        
        creative_results.append({
            "name": creative.get('name'),
            "actuals": actuals,
            "percentage": percentage,
            "daily_budget": daily_budget,
            "projected_landing": projected_landing
        })
        
    return {
        "simulation": sim,
        "net_amount": net_amount,
        "usable_amount": usable_amount,
        "creatives": creative_results,
        "total_landing": sum(c['projected_landing'] for c in creative_results)
    }

def generate_comparison(data_a, data_b):
    """2つの計算結果から差分データを生成"""
    comparison = {
        'usable_amount': {
            'a': data_a['usable_amount'],
            'b': data_b['usable_amount'],
            'diff': data_b['usable_amount'] - data_a['usable_amount']
        },
        'total_landing': {
            'a': data_a['total_landing'],
            'b': data_b['total_landing'],
            'diff': data_b['total_landing'] - data_a['total_landing']
        },
        'creatives': []
    }
    
    all_creative_names = sorted(list(set([c['name'] for c in data_a['creatives']] + [c['name'] for c in data_b['creatives']])))

    for name in all_creative_names:
        creative_a = next((c for c in data_a['creatives'] if c['name'] == name), None)
        creative_b = next((c for c in data_b['creatives'] if c['name'] == name), None)
        
        comp_creative = {'name': name}
        
        for key in ['actuals', 'daily_budget', 'projected_landing']:
            val_a = creative_a.get(key, 0) if creative_a else 0
            val_b = creative_b.get(key, 0) if creative_b else 0
            comp_creative[key] = {'a': val_a, 'b': val_b, 'diff': val_b - val_a}
            
        comparison['creatives'].append(comp_creative)
        
    return comparison

@budget_bp.route('/clients')
def list_clients():
    """クライアント一覧ページ"""
    clients = Client.query.order_by(Client.name).all()
    return render_template('client_list.html', clients=clients)

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