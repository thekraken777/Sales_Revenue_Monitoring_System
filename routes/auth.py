
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from models import db, User
from activity_logger import log_activity

auth_bp = Blueprint('auth', __name__)


@auth_bp.before_app_request
def require_password_change():
    if current_user.is_authenticated and current_user.must_change_password:
        allowed_endpoints = [
            'auth.change_password',
            'auth.logout',
            'static'
        ]

        if request.endpoint not in allowed_endpoints:
            return redirect(url_for('auth.change_password'))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.must_change_password:
            return redirect(url_for('auth.change_password'))
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user, remember=remember)

            log_activity(
                user,
                'Login',
                f'{user.username} logged into the system.'
            )

            if user.must_change_password:
                flash('Please change your temporary password for security.', 'warning')
                return redirect(url_for('auth.change_password'))

            return redirect(url_for('dashboard.index'))

        flash('Invalid username or password. Please try again.', 'danger')

    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    user = current_user._get_current_object()

    log_activity(
        user,
        'Logout',
        f'{user.username} logged out of the system.'
    )

    logout_user()

    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('auth.login'))


@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():

    if request.method == 'POST':
        current_pass = request.form.get('current_password', '')
        new_pass = request.form.get('new_password', '')
        confirm_pass = request.form.get('confirm_password', '')

        if not check_password_hash(current_user.password_hash, current_pass):
            flash('Incorrect current password.', 'danger')
            return redirect(url_for('auth.change_password'))

        if len(new_pass) < 8:
            flash('New password must contain at least 8 characters.', 'danger')
            return redirect(url_for('auth.change_password'))

        if new_pass != confirm_pass:
            flash('New passwords do not match.', 'danger')
            return redirect(url_for('auth.change_password'))

        current_user.password_hash = generate_password_hash(new_pass)
        current_user.must_change_password = False

        log_activity(
            current_user,
            'Password Changed',
            f'{current_user.username} changed their password.'
        )

        db.session.commit()

        flash('Password updated successfully!', 'success')
        return redirect(url_for('dashboard.index'))

    return render_template('change_password.html')
