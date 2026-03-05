from extensions import db
from datetime import datetime


class Application(db.Model):
    __table_args__ = (
        db.UniqueConstraint('student_id', 'drive_id', name='unique_application'),
    )
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student.id"), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey("job_position.id"), nullable=False)

    status = db.Column(db.String(20), default="Applied", nullable=False)
    interview_date = db.Column(db.DateTime, nullable=True)
    feedback = db.Column(db.Text)

    applied_on = db.Column(db.DateTime, default=datetime.utcnow)