from app import db
from app.models.academic import Subject, Module, Topic, TopicProgress
from app.models.assignment import Assignment, Submission

def get_course_progress(student_id, subject_id):
    """Calculate course progress for a student in a subject."""
    subject = Subject.query.get(subject_id)
    if not subject:
        return 0

    # Count total topics
    total_topics = db.session.query(Topic).join(Module).filter(
        Module.subject_id == subject_id,
        Topic.is_active == True,
        Module.is_active == True
    ).count()

    # Count viewed topics
    viewed_topics = db.session.query(TopicProgress).join(Topic).join(Module).filter(
        TopicProgress.student_id == student_id,
        Module.subject_id == subject_id
    ).count()

    # Count total assignments
    total_assignments = Assignment.query.filter_by(subject_id=subject_id, is_active=True).count()

    # Count completed (approved) assignments
    completed_assignments = db.session.query(Submission).join(Assignment).filter(
        Submission.student_id == student_id,
        Assignment.subject_id == subject_id,
        Submission.status == 'approved'
    ).count()

    total = total_topics + total_assignments
    if total == 0:
        return 0

    completed = viewed_topics + completed_assignments
    return round((completed / total) * 100)


def get_student_assignment_status(student_id, assignment_id):
    """Get the latest submission status for a student's assignment."""
    sub = Submission.query.filter_by(
        student_id=student_id,
        assignment_id=assignment_id
    ).order_by(Submission.attempt_number.desc()).first()
    if not sub:
        return 'not_submitted'
    return sub.status
