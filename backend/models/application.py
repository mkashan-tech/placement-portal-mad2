from .db import db

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student.id"))
    drive_id = db.Column(db.Integer, db.ForeignKey("placement_drive.id"))
    status = db.Column(db.String(20))
    applied_on = db.Column(db.String(50))
