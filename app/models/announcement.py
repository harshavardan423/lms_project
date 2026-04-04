from app import db
from datetime import datetime

class Announcement(db.Model):
    __tablename__ = 'announcements'
    id = db.Column(db.Integer, primary_key=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    scope = db.Column(db.String(10), nullable=False)  # school, class
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=True)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id'))
    block_id = db.Column(db.Integer, db.ForeignKey('blocks.id'))
    district_id = db.Column(db.Integer, db.ForeignKey('districts.id'))
    title = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False)
    channel = db.Column(db.String(10), default='in_app')  # in_app, email, sms
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    creator = db.relationship('User', backref='announcements')
    class_ref = db.relationship('Class', backref='announcements')

class NotificationLog(db.Model):
    __tablename__ = 'notification_log'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    announcement_id = db.Column(db.Integer, db.ForeignKey('announcements.id'))
    channel = db.Column(db.String(10))
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='sent')
