from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import login_required, current_user
from datetime import datetime
import json
from app import db
from app.models.academic import Subject, Module, Topic, TopicProgress, Class, StudentClass
from app.models.assignment import Assignment, Question, Submission, SubmissionAnswer
from app.models.announcement import Announcement
from app.services.rbac import require_role
from app.services.progress import get_course_progress, get_student_assignment_status
from app.services.ai_service import evaluate_descriptive, evaluate_mcq_wrong

student_bp = Blueprint('student', __name__)

def get_student_class():
    sc = StudentClass.query.filter_by(student_id=current_user.id).first()
    return sc.class_ref if sc else None

@student_bp.route('/dashboard')
@login_required
@require_role('student')
def dashboard():
    cls = get_student_class()
    subjects = []
    if cls:
        subjects = Subject.query.filter_by(class_id=cls.id, is_active=True).all()
    announcements = Announcement.query.filter_by(school_id=current_user.school_id, is_active=True).order_by(Announcement.created_at.desc()).limit(5).all()
    recent_submissions = Submission.query.filter_by(student_id=current_user.id).order_by(Submission.submitted_at.desc()).limit(5).all()
    progress_data = {s.id: get_course_progress(current_user.id, s.id) for s in subjects}
    return render_template('student/dashboard.html', subjects=subjects, announcements=announcements,
                           recent_submissions=recent_submissions, progress_data=progress_data, cls=cls)

@student_bp.route('/courses')
@login_required
@require_role('student')
def courses():
    cls = get_student_class()
    subjects = Subject.query.filter_by(class_id=cls.id, is_active=True).all() if cls else []
    progress_data = {s.id: get_course_progress(current_user.id, s.id) for s in subjects}
    return render_template('student/courses.html', subjects=subjects, progress_data=progress_data, cls=cls)

@student_bp.route('/courses/<int:subject_id>')
@login_required
@require_role('student')
def course_detail(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    modules = Module.query.filter_by(subject_id=subject_id, is_active=True).order_by(Module.order).all()
    viewed_ids = {tp.topic_id for tp in TopicProgress.query.filter_by(student_id=current_user.id).all()}
    progress = get_course_progress(current_user.id, subject_id)
    return render_template('student/course_detail.html', subject=subject, modules=modules,
                           viewed_ids=viewed_ids, progress=progress)

@student_bp.route('/courses/<int:subject_id>/topics/<int:topic_id>', methods=['GET', 'POST'])
@login_required
@require_role('student')
def topic_view(subject_id, topic_id):
    subject = Subject.query.get_or_404(subject_id)
    topic = Topic.query.get_or_404(topic_id)
    # Mark as viewed
    existing = TopicProgress.query.filter_by(student_id=current_user.id, topic_id=topic_id).first()
    if not existing:
        tp = TopicProgress(student_id=current_user.id, topic_id=topic_id)
        db.session.add(tp); db.session.commit()
    return render_template('student/topic_view.html', subject=subject, topic=topic)

@student_bp.route('/assignments')
@login_required
@require_role('student')
def assignments():
    cls = get_student_class()
    if not cls:
        return render_template('student/assignments.html', assignments=[], now=datetime.utcnow())
    assignments = Assignment.query.filter_by(class_id=cls.id, is_active=True).order_by(Assignment.deadline).all()
    status_map = {a.id: get_student_assignment_status(current_user.id, a.id) for a in assignments}
    return render_template('student/assignments.html', assignments=assignments, status_map=status_map, now=datetime.utcnow())

@student_bp.route('/assignments/<int:id>/attempt', methods=['GET', 'POST'])
@login_required
@require_role('student')
def attempt_assignment(id):
    assignment = Assignment.query.get_or_404(id)
    # Deadline check
    if datetime.utcnow() > assignment.deadline:
        flash('This assignment deadline has passed.', 'danger')
        return redirect(url_for('student.assignments'))
    # Attempt check
    existing_subs = Submission.query.filter_by(student_id=current_user.id, assignment_id=id).count()
    if existing_subs >= assignment.max_attempts:
        flash('You have used all attempts for this assignment.', 'warning')
        return redirect(url_for('student.assignments'))

    questions = Question.query.filter_by(assignment_id=id, is_active=True).order_by(Question.order).all()

    if request.method == 'POST':
        submission = Submission(
            assignment_id=id,
            student_id=current_user.id,
            attempt_number=existing_subs + 1,
            status='pending_review'
        )
        db.session.add(submission); db.session.flush()

        total_ai_score = 0
        for q in questions:
            answer_text = request.form.get(f'answer_{q.id}', '')
            is_correct = False
            ai_score = None
            ai_feedback = None

            if q.type == 'mcq':
                is_correct = answer_text == q.correct_answer
                ai_score = q.marks if is_correct else 0
                if not is_correct:
                    result = evaluate_mcq_wrong(q.text, q.correct_answer)
                    ai_feedback = result.get('explanation', '')
            elif q.type == 'multi_select':
                try:
                    selected = json.loads(answer_text) if answer_text else []
                    correct = json.loads(q.correct_answer) if q.correct_answer else []
                    correct_selected = len(set(selected) & set(correct))
                    ai_score = (correct_selected / len(correct)) * q.marks if correct else 0
                    is_correct = set(selected) == set(correct)
                    if not is_correct:
                        result = evaluate_mcq_wrong(q.text, ', '.join(correct))
                        ai_feedback = result.get('explanation', '')
                except:
                    ai_score = 0
            elif q.type == 'numerical':
                try:
                    val = float(answer_text)
                    expected = float(q.correct_answer)
                    tol = q.tolerance or 0
                    is_correct = abs(val - expected) <= tol
                    ai_score = q.marks if is_correct else 0
                except:
                    ai_score = 0
            elif q.type == 'descriptive':
                result = evaluate_descriptive(q.text, answer_text)
                ai_score = (result['score'] / 10) * q.marks
                ai_feedback = result['feedback']
                is_correct = ai_score >= q.marks * 0.5
            else:  # file_upload
                ai_score = q.marks * 0.5  # default half marks for file submission
                is_correct = True

            total_ai_score += ai_score or 0
            sa = SubmissionAnswer(
                submission_id=submission.id,
                question_id=q.id,
                answer_text=answer_text,
                ai_score=ai_score,
                ai_feedback=ai_feedback,
                is_correct=is_correct
            )
            db.session.add(sa)

        db.session.commit()
        flash('Assignment submitted successfully! Awaiting teacher review.', 'success')
        return redirect(url_for('student.assignments'))

    return render_template('student/attempt_assignment.html', assignment=assignment, questions=questions)

@student_bp.route('/assignments/<int:id>/report')
@login_required
@require_role('student')
def assignment_report(id):
    submission = Submission.query.filter_by(assignment_id=id, student_id=current_user.id, status='approved').order_by(Submission.attempt_number.desc()).first()
    if not submission:
        flash('Report not available yet. Waiting for teacher approval.', 'info')
        return redirect(url_for('student.assignments'))
    assignment = submission.assignment
    total_marks = sum(q.marks for q in assignment.questions if q.is_active)
    return render_template('student/report.html', submission=submission, assignment=assignment, total_marks=total_marks)
