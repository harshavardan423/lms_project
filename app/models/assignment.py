from app import db
from datetime import datetime

class Assignment(db.Model):
    __tablename__ = 'assignments'
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    instructions = db.Column(db.Text)
    deadline = db.Column(db.DateTime, nullable=False)
    max_attempts = db.Column(db.Integer, default=1)
    allow_retry = db.Column(db.Boolean, default=False)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id'))
    block_id = db.Column(db.Integer, db.ForeignKey('blocks.id'))
    district_id = db.Column(db.Integer, db.ForeignKey('districts.id'))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    subject = db.relationship('Subject', backref='assignments')
    class_ref = db.relationship('Class', backref='assignments')
    teacher = db.relationship('User', backref='created_assignments')
    questions = db.relationship('Question', backref='assignment', lazy=True, order_by='Question.order')

class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.id'), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # mcq, multi_select, descriptive, numerical, file_upload
    text = db.Column(db.Text, nullable=False)
    marks = db.Column(db.Float, default=1.0)
    correct_answer = db.Column(db.Text)  # JSON for MCQ options/correct; plain text for others
    options = db.Column(db.Text)  # JSON array for MCQ/multi_select
    tolerance = db.Column(db.Float, nullable=True)
    order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)

class Submission(db.Model):
    __tablename__ = 'submissions'
    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    attempt_number = db.Column(db.Integer, default=1)
    status = db.Column(db.String(20), default='submitted')  # submitted, pending_review, approved
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    teacher_approved_at = db.Column(db.DateTime)
    final_score = db.Column(db.Float)
    teacher_feedback = db.Column(db.Text)
    assignment = db.relationship('Assignment', backref='submissions')
    student = db.relationship('User', backref='submissions')
    answers = db.relationship('SubmissionAnswer', backref='submission', lazy=True)

class SubmissionAnswer(db.Model):
    __tablename__ = 'submission_answers'
    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey('submissions.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    answer_text = db.Column(db.Text)
    file_path = db.Column(db.String(300))
    ai_score = db.Column(db.Float)
    ai_feedback = db.Column(db.Text)
    teacher_score = db.Column(db.Float)
    teacher_override = db.Column(db.Boolean, default=False)
    is_correct = db.Column(db.Boolean)
    question = db.relationship('Question', backref='answers')
