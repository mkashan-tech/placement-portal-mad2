from .db import db

class JobPosition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("company.id"))
    title = db.Column(db.String(120))
    salary = db.Column(db.Integer)
    skills_required = db.Column(db.String(200))
    description = db.Column(db.Text)
