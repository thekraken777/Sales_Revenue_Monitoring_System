from werkzeug.security import generate_password_hash
from app import app
from models import db, User

with app.app_context():
    admin = User.query.filter_by(username='admin').first()

    if admin:
        admin.password_hash = generate_password_hash('Admin@123')
        admin.must_change_password = True
        db.session.commit()
        print("Admin password reset successfully!")
    else:
        print("Admin account not found.")