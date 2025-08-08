from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import db
from .models import Client, BudgetSimulation

budget_bp = Blueprint('budget', __name__, template_folder='templates')

@budget_bp.route('/')
def list_simulations():
    simulations = BudgetSimulation.query.all()
    return render_template('budget/list.html', simulations=simulations)

@budget_bp.route('/clients')
def client_list():
    clients = Client.query.all()
    return render_template('budget/client_list.html', clients=clients)

@budget_bp.route('/add_simulation', methods=['GET', 'POST'])
def add_simulation():
    if request.method == 'POST':
        new_sim = BudgetSimulation(
            client_id=request.form['client_id'],
            month=request.form['month'],
            estimated_pv=request.form.get('estimated_pv'),
            cvr=request.form.get('cvr'),
            cpa=request.form.get('cpa')
        )
        db.session.add(new_sim)
        db.session.commit()
        flash('予算シミュレーションを追加しました。')
        return redirect(url_for('budget.list_simulations'))
    
    clients = Client.query.all()
    return render_template('budget/form.html', clients=clients)

# Other routes like calculator, compare, etc. would be defined here
# based on the original app.py