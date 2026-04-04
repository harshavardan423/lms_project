from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user

ROLE_HIERARCHY = {
    'super_admin': 7,
    'district_admin': 6,
    'block_admin': 5,
    'school_admin': 4,
    'teacher': 3,
    'student': 2,
    'parent': 1,
}

def require_role(*roles):
    """Decorator to require one of the specified roles."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))
            if current_user.role not in roles:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def can_access_school(user, school_id):
    if user.role == 'super_admin':
        return True
    if user.role == 'district_admin':
        from app.models.hierarchy import School
        school = School.query.get(school_id)
        return school and school.district_id == user.district_id
    if user.role == 'block_admin':
        from app.models.hierarchy import School
        school = School.query.get(school_id)
        return school and school.block_id == user.block_id
    return user.school_id == school_id

def scope_query(query, model, user):
    """Apply hierarchy scope to a query based on user role."""
    if user.role == 'super_admin':
        return query
    if user.role == 'district_admin':
        return query.filter(model.district_id == user.district_id)
    if user.role == 'block_admin':
        return query.filter(model.block_id == user.block_id)
    if user.role in ('school_admin', 'teacher', 'student', 'parent'):
        return query.filter(model.school_id == user.school_id)
    return query.filter(False)
