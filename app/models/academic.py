from app import db
from datetime import datetime

class Class(db.Model):
    __tablename__ = 'classes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    academic_year = db.Column(db.String(20), nullable=False, default='2024-25')
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id'), nullable=False)
    block_id = db.Column(db.Integer, db.ForeignKey('blocks.id'), nullable=False)
    district_id = db.Column(db.Integer, db.ForeignKey('districts.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    school = db.relationship('School', backref='classes')
    subjects = db.relationship('Subject', backref='class_ref', lazy=True)

class ClassTeacher(db.Model):
    __tablename__ = 'class_teacher'
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    class_ref = db.relationship('Class', backref='class_teachers')
    teacher = db.relationship('User', backref='class_assignments')
    subject = db.relationship('Subject', backref='class_teachers')

class StudentClass(db.Model):
    __tablename__ = 'student_class'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    student = db.relationship('User', backref='class_enrollment')
    class_ref = db.relationship('Class', backref='students')

class Subject(db.Model):
    __tablename__ = 'subjects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id'), nullable=False)
    block_id = db.Column(db.Integer, db.ForeignKey('blocks.id'), nullable=False)
    district_id = db.Column(db.Integer, db.ForeignKey('districts.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    modules = db.relationship('Module', backref='subject', lazy=True, order_by='Module.order')

class Module(db.Model):
    __tablename__ = 'modules'
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    topics = db.relationship('Topic', backref='module', lazy=True, order_by='Topic.order')

class Topic(db.Model):
    __tablename__ = 'topics'
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content_text = db.Column(db.Text)
    file_path = db.Column(db.String(300))       # existing image field
    pdf_path = db.Column(db.String(300))         # NEW — uploaded PDF
    video_url = db.Column(db.String(500))        # NEW — YouTube / Drive embed URL
    order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)

class TopicProgress(db.Model):
    __tablename__ = 'topic_progress'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'), nullable=False)
    viewed_at = db.Column(db.DateTime, default=datetime.utcnow)
    student = db.relationship('User', backref='topic_progress')
    topic = db.relationship('Topic', backref='progress_records')
