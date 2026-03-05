from extensions import db
from datetime import datetime

class JobPosition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("company.id"))
    title = db.Column(db.String(120))
    salary = db.Column(db.Integer)
    skills_required = db.Column(db.String(200))
    description = db.Column(db.Text)
    location = db.Column(db.String(150))
    experience_required = db.Column(db.String(100))
    benefits = db.Column(db.Text)
    status = db.Column(db.String(20), default="Active")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    approved = db.Column(db.Boolean, default=False)
