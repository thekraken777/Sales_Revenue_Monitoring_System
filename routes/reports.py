from datetime import datetime, date, timedelta
from flask import Blueprint, render_template, request
from flask_login import login_required
from sqlalchemy import func
from models import db, Sale, Product

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/revenue')
@login_required
def revenue():
    filter_type = request.args.get('filter', 'this_month')
    now = datetime.now()

    query = db.session.query(
        func.sum(Sale.total_revenue).label('revenue'),
        func.sum(Sale.cost_price * Sale.quantity_sold).label('cost'),
        func.sum(Sale.total_profit).label('profit')
    )

    if filter_type == 'today':
        query = query.filter(func.date(Sale.transaction_date) == date.today())
    elif filter_type == 'this_week':
        start_week = date.today() - timedelta(days=date.today().weekday())
        query = query.filter(Sale.transaction_date >= start_week)
    elif filter_type == 'this_month':
        query = query.filter(func.extract('month', Sale.transaction_date) == now.month,
                             func.extract('year', Sale.transaction_date) == now.year)

    result = query.first()
    tot_revenue = result.revenue or 0.0
    tot_cost = result.cost or 0.0
    gross_profit = result.profit or 0.0

    return render_template('revenue.html',
                           tot_revenue=tot_revenue,
                           tot_cost=tot_cost,
                           gross_profit=gross_profit,
                           filter_type=filter_type)

@reports_bp.route('/best-sellers')
@login_required
def best_sellers():
    best_sellers_data = db.session.query(
        Product.product_name,
        Product.category,
        func.sum(Sale.quantity_sold).label('total_qty'),
        func.sum(Sale.total_revenue).label('total_revenue'),
        func.sum(Sale.total_profit).label('total_profit')
    ).join(Sale).group_by(Product.id).order_by(func.sum(Sale.quantity_sold).desc()).all()

    return render_template('best_sellers.html', best_sellers=best_sellers_data)

@reports_bp.route('/reports')
@login_required
def reports():
    report_type = request.args.get('type', 'daily')
    sales_data = Sale.query.order_by(Sale.transaction_date.desc()).all()
    
    tot_transactions = len(sales_data)
    tot_qty = sum(s.quantity_sold for s in sales_data)
    tot_revenue = sum(s.total_revenue for s in sales_data)
    tot_profit = sum(s.total_profit for s in sales_data)

    return render_template('reports.html',
                           sales=sales_data,
                           report_type=report_type,
                           tot_transactions=tot_transactions,
                           tot_qty=tot_qty,
                           tot_revenue=tot_revenue,
                           tot_profit=tot_profit)