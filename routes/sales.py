
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Sale, Product
from activity_logger import log_activity

sales_bp = Blueprint('sales', __name__)


# SALES MANAGEMENT PAGE
@sales_bp.route('/sales')
@login_required
def index():
    products = Product.query.filter(
        Product.stock_quantity > 0
    ).all()

    sales = Sale.query.order_by(
        Sale.transaction_date.desc()
    ).all()

    return render_template(
        'sales.html',
        products=products,
        sales=sales
    )


# RECORD NEW SALE
@sales_bp.route('/sales/record', methods=['POST'])
@login_required
def record_sale():
    product_id = int(request.form.get('product_id'))
    quantity_sold = int(request.form.get('quantity_sold'))

    product = Product.query.get_or_404(product_id)

    if quantity_sold <= 0:
        flash('Quantity must be greater than zero.', 'danger')
        return redirect(url_for('sales.index'))

    if quantity_sold > product.stock_quantity:
        flash(
            f'Insufficient stock! Available: {product.stock_quantity}',
            'danger'
        )
        return redirect(url_for('sales.index'))

    total_revenue = product.selling_price * quantity_sold
    total_cost = product.cost_price * quantity_sold
    total_profit = total_revenue - total_cost

    product_name = product.product_name

    new_sale = Sale(
        product_id=product.id,
        quantity_sold=quantity_sold,
        selling_price=product.selling_price,
        cost_price=product.cost_price,
        total_revenue=total_revenue,
        total_profit=total_profit,
        recorded_by=current_user.username
    )

    # Reduce product stock
    product.stock_quantity -= quantity_sold

    db.session.add(new_sale)
    db.session.commit()

    log_activity(
        current_user,
        'Sale Recorded',
        f'{current_user.username} recorded a sale of {quantity_sold} '
        f'{product_name}. Revenue: ₱{total_revenue:,.2f}, '
        f'Profit: ₱{total_profit:,.2f}.'
    )

    flash('Sale transaction recorded successfully!', 'success')
    return redirect(url_for('sales.index'))


# DELETE SALE AND RESTORE STOCK
@sales_bp.route('/sales/delete/<int:id>', methods=['POST'])
@login_required
def delete_sale(id):
    sale = Sale.query.get_or_404(id)
    product = Product.query.get(sale.product_id)

    product_name = product.product_name if product else 'Unknown product'
    quantity = sale.quantity_sold
    revenue = sale.total_revenue

    # Restore product stock
    if product:
        product.stock_quantity += quantity

    db.session.delete(sale)
    db.session.commit()

    log_activity(
        current_user,
        'Sale Deleted',
        f'{current_user.username} deleted a sale of {quantity} '
        f'{product_name}. Revenue removed: ₱{revenue:,.2f}.'
    )

    flash('Transaction deleted and inventory restored!', 'success')
    return redirect(url_for('sales.index'))
