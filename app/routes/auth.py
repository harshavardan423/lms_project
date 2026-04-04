from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User

auth_bp = Blueprint('auth', __name__)

ROLE_DASHBOARDS = {
    'super_admin': 'admin.dashboard',
    'district_admin': 'admin.dashboard',
    'block_admin': 'admin.dashboard',
    'school_admin': 'admin.dashboard',
    'teacher': 'teacher.dashboard',
    'student': 'student.dashboard',
    'parent': 'parent.dashboard',
}

@auth_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for(ROLE_DASHBOARDS.get(current_user.role, 'auth.login')))
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for(ROLE_DASHBOARDS.get(current_user.role, 'auth.login')))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        user = User.query.filter_by(username=username, is_active=True).first()
        if user and user.check_password(password):
            login_user(user)
            flash(f'Welcome back, {user.full_name}!', 'success')
            return redirect(url_for(ROLE_DASHBOARDS.get(user.role, 'auth.login')))
        flash('Invalid username or password.', 'danger')
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
