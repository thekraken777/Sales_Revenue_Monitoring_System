
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Product
from activity_logger import log_activity

products_bp = Blueprint('products', __name__)


@products_bp.route('/products')
@login_required
def index():
    search_query = request.args.get('search', '')

    if search_query:
        products = Product.query.filter(
            Product.product_name.ilike(f'%{search_query}%')
        ).all()
    else:
       products = Product.query.order_by(
    Product.id.asc()
    ).all()

    return render_template(
        'products.html',
        products=products,
        search_query=search_query
    )


@products_bp.route('/products/add', methods=['POST'])
@login_required
def add_product():
    product_name = request.form.get('product_name')
    category = request.form.get('category')
    description = request.form.get('description')
    cost_price = float(request.form.get('cost_price', 0))
    selling_price = float(request.form.get('selling_price', 0))
    stock_quantity = int(request.form.get('stock_quantity', 0))

    if Product.query.filter_by(product_name=product_name).first():
        flash('A product with this name already exists.', 'danger')
        return redirect(url_for('products.index'))

    new_product = Product(
        product_name=product_name,
        category=category,
        description=description,
        cost_price=cost_price,
        selling_price=selling_price,
        stock_quantity=stock_quantity
    )

    db.session.add(new_product)
    db.session.commit()

    log_activity(
        current_user,
        'Product Added',
        f'{current_user.username} added product: {product_name}.'
    )

    flash('Product added successfully!', 'success')
    return redirect(url_for('products.index'))


@products_bp.route('/products/edit/<int:id>', methods=['POST'])
@login_required
def edit_product(id):
    product = Product.query.get_or_404(id)

    product.product_name = request.form.get('product_name')
    product.category = request.form.get('category')
    product.description = request.form.get('description')
    product.cost_price = float(request.form.get('cost_price', 0))
    product.selling_price = float(request.form.get('selling_price', 0))
    product.stock_quantity = int(request.form.get('stock_quantity', 0))

    product_name = product.product_name

    db.session.commit()

    log_activity(
        current_user,
        'Product Updated',
        f'{current_user.username} updated product: {product_name}.'
    )

    flash('Product updated successfully!', 'success')
    return redirect(url_for('products.index'))


@products_bp.route('/products/delete/<int:id>', methods=['POST'])
@login_required
def delete_product(id):
    product = Product.query.get_or_404(id)
    product_name = product.product_name

    db.session.delete(product)
    db.session.commit()

    log_activity(
        current_user,
        'Product Deleted',
        f'{current_user.username} deleted product: {product_name}.'
    )

    flash('Product deleted successfully!', 'success')
    return redirect(url_for('products.index'))
