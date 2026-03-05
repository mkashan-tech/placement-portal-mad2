from extensions import db

class Placement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student.id"))
    company_id = db.Column(db.Integer, db.ForeignKey("company.id"))
    position = db.Column(db.String(120))
    salary = db.Column(db.Integer)
    joining_date = db.Column(db.DateTime(50))
