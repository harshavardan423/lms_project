from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from datetime import datetime
import json, os
from werkzeug.utils import secure_filename
from app import db
from app.models.academic import Subject, Module, Topic, Class, ClassTeacher
from app.models.assignment import Assignment, Question, Submission, SubmissionAnswer
from app.models.announcement import Announcement
from app.models.user import User
from app.services.rbac import require_role
from app.services.ai_service import generate_assignment_from_prompt

teacher_bp = Blueprint('teacher', __name__)

ALLOWED_PDF = {'pdf'}
ALLOWED_IMG = {'jpg', 'jpeg', 'png'}

def allowed_file(filename, allowed):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed

def save_upload(file, subfolder):
    from flask import current_app
    filename = secure_filename(file.filename)
    folder = os.path.join(current_app.config['UPLOAD_FOLDER'], subfolder)
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, filename)
    file.save(path)
    return os.path.join('uploads', subfolder, filename).replace('\\', '/')

@teacher_bp.route('/dashboard')
@login_required
@require_role('teacher')
def dashboard():
    assignments = Assignment.query.filter_by(teacher_id=current_user.id, is_active=True).order_by(Assignment.created_at.desc()).limit(5).all()
    pending_reviews = Submission.query.join(Assignment).filter(
        Assignment.teacher_id == current_user.id,
        Submission.status == 'pending_review'
    ).count()
    ct = ClassTeacher.query.filter_by(teacher_id=current_user.id).all()
    subject_ids = list({x.subject_id for x in ct})
    subjects = Subject.query.filter(Subject.id.in_(subject_ids)).all()
    return render_template('teacher/dashboard.html', assignments=assignments, pending_reviews=pending_reviews, subjects=subjects)

@teacher_bp.route('/courses')
@login_required
@require_role('teacher')
def courses():
    ct = ClassTeacher.query.filter_by(teacher_id=current_user.id).all()
    subject_ids = list({x.subject_id for x in ct})
    subjects = Subject.query.filter(Subject.id.in_(subject_ids), Subject.is_active == True).all()
    return render_template('teacher/courses.html', subjects=subjects)

@teacher_bp.route('/courses/<int:subject_id>/topics', methods=['GET', 'POST'])
@login_required
@require_role('teacher')
def course_topics(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add_module':
            m = Module(subject_id=subject_id, title=request.form['title'],
                       order=Module.query.filter_by(subject_id=subject_id).count() + 1)
            db.session.add(m); db.session.commit()
            flash('Module added.', 'success')

        elif action == 'add_topic':
            module_id = int(request.form['module_id'])
            t = Topic(
                module_id=module_id,
                title=request.form['title'],
                content_text=request.form.get('content_text', ''),
                video_url=request.form.get('video_url', '').strip() or None,
                order=Topic.query.filter_by(module_id=module_id).count() + 1
            )
            # PDF upload
            if 'pdf_file' in request.files:
                pdf = request.files['pdf_file']
                if pdf and pdf.filename and allowed_file(pdf.filename, ALLOWED_PDF):
                    t.pdf_path = save_upload(pdf, 'pdfs')
            # Image upload (existing)
            if 'image_file' in request.files:
                img = request.files['image_file']
                if img and img.filename and allowed_file(img.filename, ALLOWED_IMG):
                    t.file_path = save_upload(img, 'images')
            db.session.add(t); db.session.commit()
            flash('Topic added.', 'success')

        elif action == 'edit_topic':
            t = Topic.query.get(int(request.form['topic_id']))
            if t:
                t.title = request.form['title']
                t.content_text = request.form.get('content_text', '')
                t.video_url = request.form.get('video_url', '').strip() or None
                t.module_id = int(request.form['module_id'])
                # PDF — remove if checkbox ticked, replace if new file uploaded
                if request.form.get('remove_pdf'):
                    t.pdf_path = None
                elif 'pdf_file' in request.files:
                    pdf = request.files['pdf_file']
                    if pdf and pdf.filename and allowed_file(pdf.filename, ALLOWED_PDF):
                        t.pdf_path = save_upload(pdf, 'pdfs')
                # Image — remove if checkbox ticked, replace if new file uploaded
                if request.form.get('remove_image'):
                    t.file_path = None
                elif 'image_file' in request.files:
                    img = request.files['image_file']
                    if img and img.filename and allowed_file(img.filename, ALLOWED_IMG):
                        t.file_path = save_upload(img, 'images')
                db.session.commit()
                flash('Topic updated.', 'success')

        elif action == 'delete_topic':
            t = Topic.query.get(int(request.form['topic_id']))
            if t:
                t.is_active = False
                db.session.commit()
                flash('Topic removed.', 'warning')

        elif action == 'edit_module':
            m = Module.query.get(int(request.form['module_id']))
            if m:
                m.title = request.form['title']
                db.session.commit()
                flash('Module renamed.', 'success')

        elif action == 'delete_module':
            m = Module.query.get(int(request.form['module_id']))
            if m:
                for t in m.topics:
                    t.is_active = False
                m.is_active = False
                db.session.commit()
                flash('Module and its topics removed.', 'warning')

    modules = Module.query.filter_by(subject_id=subject_id, is_active=True).order_by(Module.order).all()
    return render_template('teacher/course_topics.html', subject=subject, modules=modules)

@teacher_bp.route('/assignments', methods=['GET', 'POST'])
@login_required
@require_role('teacher')
def assignments():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'delete':
            a = Assignment.query.get(int(request.form['assignment_id']))
            if a and a.teacher_id == current_user.id:
                a.is_active = False
                db.session.commit()
                flash('Assignment deleted.', 'warning')

        elif action == 'create':
            deadline = datetime.strptime(request.form['deadline'], '%Y-%m-%dT%H:%M')
            cls = Class.query.get(int(request.form['class_id']))
            a = Assignment(
                subject_id=int(request.form['subject_id']),
                class_id=cls.id,
                teacher_id=current_user.id,
                title=request.form['title'],
                instructions=request.form.get('instructions', ''),
                deadline=deadline,
                max_attempts=int(request.form.get('max_attempts', 1)),
                school_id=current_user.school_id,
                block_id=current_user.block_id,
                district_id=current_user.district_id
            )
            db.session.add(a); db.session.commit()
            flash('Assignment created. Now add questions.', 'success')
            return redirect(url_for('teacher.assignment_questions', id=a.id))
    ct = ClassTeacher.query.filter_by(teacher_id=current_user.id).all()
    subject_ids = list({x.subject_id for x in ct})
    class_ids = list({x.class_id for x in ct})
    subjects = Subject.query.filter(Subject.id.in_(subject_ids)).all()
    classes = Class.query.filter(Class.id.in_(class_ids)).all()
    assignments = Assignment.query.filter_by(teacher_id=current_user.id, is_active=True).order_by(Assignment.created_at.desc()).all()
    return render_template('teacher/assignments.html', assignments=assignments, subjects=subjects, classes=classes)

@teacher_bp.route('/assignments/<int:id>/questions', methods=['GET', 'POST'])
@login_required
@require_role('teacher')
def assignment_questions(id):
    assignment = Assignment.query.get_or_404(id)
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'add_question':
            q = Question(
                assignment_id=id,
                type=request.form['type'],
                text=request.form['text'],
                marks=float(request.form.get('marks', 1)),
                correct_answer=request.form.get('correct_answer', ''),
                options=request.form.get('options', ''),
                tolerance=float(request.form['tolerance']) if request.form.get('tolerance') else None,
                order=Question.query.filter_by(assignment_id=id).count() + 1
            )
            db.session.add(q); db.session.commit()
            flash('Question added.', 'success')

        elif action == 'delete_question':
            q = Question.query.get(int(request.form['question_id']))
            if q: q.is_active = False; db.session.commit()

        elif action == 'ai_generate':
            # AI generates a full assignment from free-form prompt
            prompt = request.form.get('ai_prompt', '').strip()
            if not prompt:
                flash('Please enter a prompt for the AI.', 'warning')
            else:
                try:
                    result = generate_assignment_from_prompt(prompt, assignment.subject.name)
                    # Update assignment title and instructions if AI provided better ones
                    if result.get('title') and not assignment.questions:
                        assignment.title = result['title']
                        assignment.instructions = result.get('instructions', assignment.instructions)
                    # Add all generated questions
                    start_order = Question.query.filter_by(assignment_id=id).count() + 1
                    for i, qdata in enumerate(result.get('questions', [])):
                        opts = qdata.get('options')
                        q = Question(
                            assignment_id=id,
                            type=qdata['type'],
                            text=qdata['text'],
                            marks=float(qdata.get('marks', 2)),
                            correct_answer=str(qdata.get('correct_answer', '')),
                            options=json.dumps(opts) if opts else None,
                            tolerance=qdata.get('tolerance'),
                            order=start_order + i
                        )
                        db.session.add(q)
                    db.session.commit()
                    flash(f'AI generated {len(result.get("questions", []))} questions successfully!', 'success')
                except Exception as e:
                    flash(f'AI generation failed: {str(e)}', 'danger')

    questions = Question.query.filter_by(assignment_id=id, is_active=True).order_by(Question.order).all()
    return render_template('teacher/assignment_questions.html', assignment=assignment, questions=questions)

@teacher_bp.route('/assignments/<int:id>/submissions')
@login_required
@require_role('teacher')
def assignment_submissions(id):
    assignment = Assignment.query.get_or_404(id)
    submissions = Submission.query.filter_by(assignment_id=id).order_by(Submission.submitted_at.desc()).all()
    return render_template('teacher/submissions.html', assignment=assignment, submissions=submissions)

@teacher_bp.route('/submissions/<int:id>/review', methods=['GET', 'POST'])
@login_required
@require_role('teacher')
def review_submission(id):
    submission = Submission.query.get_or_404(id)
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'approve':
            total_score = 0
            for answer in submission.answers:
                q_id = str(answer.question_id)
                ts = request.form.get(f'teacher_score_{q_id}')
                if ts is not None:
                    answer.teacher_score = float(ts)
                    answer.teacher_override = True
                    total_score += float(ts)
                elif answer.ai_score is not None:
                    total_score += answer.ai_score
            submission.final_score = total_score
            submission.teacher_feedback = request.form.get('teacher_feedback', '')
            submission.status = 'approved'
            submission.teacher_approved_at = datetime.utcnow()
            db.session.commit()
            flash('Submission approved!', 'success')
            return redirect(url_for('teacher.assignment_submissions', id=submission.assignment_id))
    return render_template('teacher/review_submission.html', submission=submission)

@teacher_bp.route('/announcements', methods=['GET', 'POST'])
@login_required
@require_role('teacher')
def announcements():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'create':
            a = Announcement(
                created_by=current_user.id,
                scope=request.form['scope'],
                class_id=request.form.get('class_id') or None,
                school_id=current_user.school_id,
                block_id=current_user.block_id,
                district_id=current_user.district_id,
                title=request.form['title'],
                body=request.form['body']
            )
            db.session.add(a); db.session.commit()
            flash('Announcement posted.', 'success')
    ct = ClassTeacher.query.filter_by(teacher_id=current_user.id).all()
    class_ids = list({x.class_id for x in ct})
    classes = Class.query.filter(Class.id.in_(class_ids)).all()
    announcements = Announcement.query.filter_by(school_id=current_user.school_id, is_active=True).order_by(Announcement.created_at.desc()).all()
    return render_template('teacher/announcements.html', announcements=announcements, classes=classes)
