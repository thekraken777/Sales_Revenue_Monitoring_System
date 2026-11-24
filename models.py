from datetime import datetime
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='staff') # 'admin' or 'staff'
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    must_change_password = db.Column(db.Boolean, default=False)

    def get_id(self):
        return str(self.id)

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(120), unique=True, nullable=False)
    category = db.Column(db.String(60), nullable=False)
    description = db.Column(db.Text, nullable=True)
    cost_price = db.Column(db.Float, nullable=False)
    selling_price = db.Column(db.Float, nullable=False)
    stock_quantity = db.Column(db.Integer, nullable=False, default=0)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def profit_per_unit(self):
        return self.selling_price - self.cost_price

class Sale(db.Model):
    __tablename__ = 'sales'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity_sold = db.Column(db.Integer, nullable=False)
    selling_price = db.Column(db.Float, nullable=False)
    cost_price = db.Column(db.Float, nullable=False)
    total_revenue = db.Column(db.Float, nullable=False)
    total_profit = db.Column(db.Float, nullable=False)
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow)
    recorded_by = db.Column(db.String(80), nullable=False)

    product = db.relationship('Product', backref=db.backref('sales', cascade='all, delete-orphan'))

class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='SET NULL'),
        nullable=True
    )

    username = db.Column(db.String(80), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='activity_logs')
