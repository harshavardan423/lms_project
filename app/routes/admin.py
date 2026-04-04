from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.hierarchy import District, Block, School
from app.models.user import User, ParentStudent
from app.models.academic import Class, Subject, ClassTeacher, StudentClass
from app.services.rbac import require_role

admin_bp = Blueprint('admin', __name__)

ADMIN_ROLES = ('super_admin', 'district_admin', 'block_admin', 'school_admin')

@admin_bp.route('/dashboard')
@login_required
@require_role(*ADMIN_ROLES)
def dashboard():
    stats = {}
    if current_user.role == 'super_admin':
        stats['districts'] = District.query.filter_by(is_active=True).count()
        stats['blocks'] = Block.query.filter_by(is_active=True).count()
        stats['schools'] = School.query.filter_by(is_active=True).count()
        stats['users'] = User.query.filter_by(is_active=True).count()
    elif current_user.role == 'district_admin':
        stats['blocks'] = Block.query.filter_by(district_id=current_user.district_id, is_active=True).count()
        stats['schools'] = School.query.filter_by(district_id=current_user.district_id, is_active=True).count()
        stats['users'] = User.query.filter_by(district_id=current_user.district_id, is_active=True).count()
    elif current_user.role == 'block_admin':
        stats['schools'] = School.query.filter_by(block_id=current_user.block_id, is_active=True).count()
        stats['users'] = User.query.filter_by(block_id=current_user.block_id, is_active=True).count()
    else:  # school_admin
        stats['teachers'] = User.query.filter_by(school_id=current_user.school_id, role='teacher', is_active=True).count()
        stats['students'] = User.query.filter_by(school_id=current_user.school_id, role='student', is_active=True).count()
        stats['classes'] = Class.query.filter_by(school_id=current_user.school_id, is_active=True).count()
    return render_template('admin/dashboard.html', stats=stats)

@admin_bp.route('/districts', methods=['GET', 'POST'])
@login_required
@require_role('super_admin')
def districts():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'create':
            d = District(name=request.form['name'])
            db.session.add(d); db.session.commit()
            flash('District created.', 'success')
        elif action == 'delete':
            d = District.query.get(request.form['id'])
            if d: d.is_active = False; db.session.commit()
            flash('District deactivated.', 'warning')
    districts = District.query.filter_by(is_active=True).all()
    return render_template('admin/districts.html', districts=districts)

@admin_bp.route('/blocks', methods=['GET', 'POST'])
@login_required
@require_role('super_admin', 'district_admin')
def blocks():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'create':
            b = Block(name=request.form['name'], district_id=int(request.form['district_id']))
            db.session.add(b); db.session.commit()
            flash('Block created.', 'success')
        elif action == 'delete':
            b = Block.query.get(request.form['id'])
            if b: b.is_active = False; db.session.commit()
            flash('Block deactivated.', 'warning')
    if current_user.role == 'super_admin':
        blocks = Block.query.filter_by(is_active=True).all()
    else:
        blocks = Block.query.filter_by(district_id=current_user.district_id, is_active=True).all()
    districts = District.query.filter_by(is_active=True).all()
    return render_template('admin/blocks.html', blocks=blocks, districts=districts)

@admin_bp.route('/schools', methods=['GET', 'POST'])
@login_required
@require_role('super_admin', 'district_admin', 'block_admin')
def schools():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'create':
            block = Block.query.get(int(request.form['block_id']))
            s = School(name=request.form['name'], block_id=block.id, district_id=block.district_id)
            db.session.add(s); db.session.commit()
            flash('School created.', 'success')
        elif action == 'delete':
            s = School.query.get(request.form['id'])
            if s: s.is_active = False; db.session.commit()
    if current_user.role == 'super_admin':
        schools = School.query.filter_by(is_active=True).all()
        blocks = Block.query.filter_by(is_active=True).all()
    elif current_user.role == 'district_admin':
        schools = School.query.filter_by(district_id=current_user.district_id, is_active=True).all()
        blocks = Block.query.filter_by(district_id=current_user.district_id, is_active=True).all()
    else:
        schools = School.query.filter_by(block_id=current_user.block_id, is_active=True).all()
        blocks = Block.query.filter_by(id=current_user.block_id, is_active=True).all()
    return render_template('admin/schools.html', schools=schools, blocks=blocks)

@admin_bp.route('/users', methods=['GET', 'POST'])
@login_required
@require_role(*ADMIN_ROLES)
def users():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'create':
            u = User(
                username=request.form['username'],
                full_name=request.form['full_name'],
                email=request.form.get('email'),
                role=request.form['role'],
                district_id=request.form.get('district_id') or None,
                block_id=request.form.get('block_id') or None,
                school_id=request.form.get('school_id') or None,
            )
            u.set_password(request.form['password'])
            db.session.add(u); db.session.commit()
            flash(f'User {u.username} created.', 'success')
        elif action == 'delete':
            u = User.query.get(request.form['id'])
            if u: u.is_active = False; db.session.commit()
    # Scope users
    q = User.query.filter_by(is_active=True)
    if current_user.role == 'district_admin':
        q = q.filter_by(district_id=current_user.district_id)
    elif current_user.role == 'block_admin':
        q = q.filter_by(block_id=current_user.block_id)
    elif current_user.role == 'school_admin':
        q = q.filter_by(school_id=current_user.school_id)
    users = q.all()
    districts = District.query.filter_by(is_active=True).all()
    blocks = Block.query.filter_by(is_active=True).all()
    schools = School.query.filter_by(is_active=True).all()
    return render_template('admin/users.html', users=users, districts=districts, blocks=blocks, schools=schools)

@admin_bp.route('/classes', methods=['GET', 'POST'])
@login_required
@require_role('super_admin', 'school_admin')
def classes():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'create':
            school_id = request.form.get('school_id') or current_user.school_id
            school = School.query.get(int(school_id))
            c = Class(
                name=request.form['name'],
                academic_year=request.form.get('academic_year', '2024-25'),
                school_id=school.id, block_id=school.block_id, district_id=school.district_id
            )
            db.session.add(c); db.session.commit()
            flash('Class created.', 'success')
    if current_user.role == 'super_admin':
        classes = Class.query.filter_by(is_active=True).all()
    else:
        classes = Class.query.filter_by(school_id=current_user.school_id, is_active=True).all()
    schools = School.query.filter_by(is_active=True).all()
    return render_template('admin/classes.html', classes=classes, schools=schools)

@admin_bp.route('/subjects', methods=['GET', 'POST'])
@login_required
@require_role('super_admin', 'school_admin')
def subjects():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'create':
            cls = Class.query.get(int(request.form['class_id']))
            s = Subject(
                name=request.form['name'], class_id=cls.id,
                school_id=cls.school_id, block_id=cls.block_id, district_id=cls.district_id
            )
            db.session.add(s); db.session.commit()
            flash('Subject created.', 'success')
    if current_user.role == 'super_admin':
        subjects = Subject.query.filter_by(is_active=True).all()
        classes = Class.query.filter_by(is_active=True).all()
    else:
        classes = Class.query.filter_by(school_id=current_user.school_id, is_active=True).all()
        class_ids = [c.id for c in classes]
        subjects = Subject.query.filter(Subject.class_id.in_(class_ids), Subject.is_active == True).all()
    return render_template('admin/subjects.html', subjects=subjects, classes=classes)
