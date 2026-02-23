from .db import db
from datetime import datetime

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student.id"))
    drive_id = db.Column(db.Integer, db.ForeignKey("job_position.id"))

    status = db.Column(db.String(20), default="Applied")
    interview_date = db.Column(db.String(50))
    feedback = db.Column(db.Text)

    applied_on = db.Column(db.DateTime, default=datetime.utcnow)