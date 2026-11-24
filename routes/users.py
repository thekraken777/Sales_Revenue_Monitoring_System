
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from models import db, User, ActivityLog
from activity_logger import log_activity

users_bp = Blueprint('users', __name__)


# USER MANAGEMENT PAGE
@users_bp.route('/users')
@login_required
def index():
    if current_user.role != 'admin':
        flash('Access restricted to administrators only.', 'danger')
        return redirect(url_for('dashboard.index'))

    users = User.query.all()
    return render_template('users.html', users=users)


# ADD NEW USER
@users_bp.route('/users/add', methods=['POST'])
@login_required
def add_user():
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard.index'))

    username = request.form.get('username', '').strip()
    full_name = request.form.get('full_name', '').strip()
    password = request.form.get('password', '')
    role = request.form.get('role', 'staff')

    if not username or not full_name or not password:
        flash('Please complete all fields.', 'danger')
        return redirect(url_for('users.index'))

    if len(password) < 8:
        flash('Password must contain at least 8 characters.', 'danger')
        return redirect(url_for('users.index'))

    if role not in ['admin', 'staff']:
        flash('Invalid user role.', 'danger')
        return redirect(url_for('users.index'))

    if User.query.filter_by(username=username).first():
        flash('Username already exists.', 'danger')
        return redirect(url_for('users.index'))

    new_user = User(
        username=username,
        full_name=full_name,
        password_hash=generate_password_hash(password),
        role=role
    )

    db.session.add(new_user)
    db.session.commit()

    log_activity(
        current_user,
        'User Added',
        f'{current_user.username} created a {role} account for {username}.'
    )

    flash('User account created successfully!', 'success')
    return redirect(url_for('users.index'))


# RESET STAFF PASSWORD
@users_bp.route('/users/reset-password/<int:id>', methods=['POST'])
@login_required
def reset_password(id):
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard.index'))

    user = User.query.get_or_404(id)

    if user.role != 'staff':
        flash('Only staff passwords can be reset here.', 'warning')
        return redirect(url_for('users.index'))

    new_password = request.form.get('new_password', '')

    if len(new_password) < 8:
        flash('Temporary password must contain at least 8 characters.', 'danger')
        return redirect(url_for('users.index'))

    user.password_hash = generate_password_hash(new_password)
    user.must_change_password = True

    db.session.commit()

    log_activity(
        current_user,
        'Password Reset',
        f'{current_user.username} reset the password for staff account {user.username}.'
    )

    flash(
        f'Password reset successfully for {user.username}. They must change it after logging in.',
        'success'
    )

    return redirect(url_for('users.index'))


# DELETE USER
@users_bp.route('/users/delete/<int:id>', methods=['POST'])
@login_required
def delete_user(id):
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard.index'))

    user = User.query.get_or_404(id)

    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'warning')
        return redirect(url_for('users.index'))

    deleted_username = user.username

    db.session.delete(user)
    db.session.commit()

    log_activity(
        current_user,
        'User Deleted',
        f'{current_user.username} deleted user account {deleted_username}.'
    )

    flash('User deleted successfully.', 'success')
    return redirect(url_for('users.index'))


# SETTINGS PAGE
@users_bp.route('/settings')
@login_required
def settings():
    return render_template('settings.html')


# ACTIVITY LOGS PAGE
@users_bp.route('/activity-logs')
@login_required
def activity_logs():
    if current_user.role != 'admin':
        flash('Access restricted to administrators only.', 'danger')
        return redirect(url_for('dashboard.index'))

    logs = ActivityLog.query.order_by(
        ActivityLog.timestamp.desc(),
        ActivityLog.id.desc()
    ).all()

    return render_template('activity_logs.html', logs=logs)



# CLEAR ACTIVITY LOGS
@users_bp.route('/activity-logs/clear', methods=['POST'])
@login_required
def clear_activity_logs():
    if current_user.role != 'admin':
        flash('Access restricted to administrators only.', 'danger')
        return redirect(url_for('dashboard.index'))

    ActivityLog.query.delete()
    db.session.commit()

    log_activity(
        current_user,
        'History Cleared',
        'Administrator cleared the activity history.'
    )

    flash('Activity history cleared successfully.', 'success')
    return redirect(url_for('users.activity_logs'))
