import os
from werkzeug.security import generate_password_hash
from app import app
from models import db, User, Product

def init_database():
    with app.app_context():
        # Ensure database directory exists
        db_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'database')
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)
            
        db.drop_all()
        db.create_all()
        
        # Create default Admin account
        admin_user = User(
            username='admin',
            password_hash=generate_password_hash('Admin@123'),
            full_name='System Administrator',
            role='admin',
            must_change_password=True
        )
        db.session.add(admin_user)
        
        # Create default Staff account
        staff_user = User(
            username='staff',
            password_hash=generate_password_hash('Staff@123'),
            full_name='Store Staff',
            role='staff',
            must_change_password=False
        )
        db.session.add(staff_user)
        
        # Add sample products
        sample_products = [
            Product(product_name='Wireless Mouse', category='Electronics', description='Ergonomic wireless mouse', cost_price=15.00, selling_price=29.99, stock_quantity=50),
            Product(product_name='Mechanical Keyboard', category='Electronics', description='RGB mechanical gaming keyboard', cost_price=45.00, selling_price=89.99, stock_quantity=30),
            Product(product_name='HD Monitor 24-inch', category='Electronics', description='1080p IPS computer monitor', cost_price=90.00, selling_price=149.99, stock_quantity=15),
            Product(product_name='USB-C Hub', category='Accessories', description='Multiport adapter with HDMI and USB 3.0', cost_price=12.00, selling_price=24.99, stock_quantity=40),
            Product(product_name='Gaming Headset', category='Electronics', description='Surround sound headset with mic', cost_price=25.00, selling_price=49.99, stock_quantity=25)
        ]
        
        for p in sample_products:
            db.session.add(p)
            
        db.session.commit()
        print("Database initialized successfully!")
        print("Default Admin Credentials -> Username: admin | Password: Admin@123 (Change required upon first login)")
        print("Default Staff Credentials -> Username: staff | Password: Staff@123")

if __name__ == '__main__':
    init_database()