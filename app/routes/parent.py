from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.user import User, ParentStudent
from app.models.assignment import Submission, Assignment
from app.models.announcement import Announcement
from app.models.academic import Subject, StudentClass
from app.services.rbac import require_role
from app.services.progress import get_course_progress

parent_bp = Blueprint('parent', __name__)

def get_children():
    links = ParentStudent.query.filter_by(parent_id=current_user.id).all()
    return [link.student for link in links]

@parent_bp.route('/dashboard')
@login_required
@require_role('parent')
def dashboard():
    children = get_children()
    announcements = Announcement.query.filter_by(school_id=current_user.school_id, is_active=True).order_by(Announcement.created_at.desc()).limit(5).all()
    return render_template('parent/dashboard.html', children=children, announcements=announcements)

@parent_bp.route('/children/<int:student_id>/progress')
@login_required
@require_role('parent')
def child_progress(student_id):
    # Verify this is parent's child
    link = ParentStudent.query.filter_by(parent_id=current_user.id, student_id=student_id).first()
    if not link:
        flash('Access denied.', 'danger')
        return redirect(url_for('parent.dashboard'))
    student = link.student
    sc = StudentClass.query.filter_by(student_id=student_id).first()
    subjects = []
    progress_data = {}
    if sc:
        subjects = Subject.query.filter_by(class_id=sc.class_id, is_active=True).all()
        progress_data = {s.id: get_course_progress(student_id, s.id) for s in subjects}
    return render_template('parent/child_progress.html', student=student, subjects=subjects, progress_data=progress_data)

@parent_bp.route('/children/<int:student_id>/reports')
@login_required
@require_role('parent')
def child_reports(student_id):
    link = ParentStudent.query.filter_by(parent_id=current_user.id, student_id=student_id).first()
    if not link:
        flash('Access denied.', 'danger')
        return redirect(url_for('parent.dashboard'))
    student = link.student
    submissions = Submission.query.filter_by(student_id=student_id, status='approved').order_by(Submission.submitted_at.desc()).all()
    return render_template('parent/child_reports.html', student=student, submissions=submissions)

@parent_bp.route('/announcements')
@login_required
@require_role('parent')
def announcements():
    announcements = Announcement.query.filter_by(school_id=current_user.school_id, is_active=True).order_by(Announcement.created_at.desc()).all()
    return render_template('parent/announcements.html', announcements=announcements)
