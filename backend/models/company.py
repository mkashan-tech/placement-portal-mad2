from .db import db
class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    company_name = db.Column(db.String(120))
    website = db.Column(db.String(120))
    hr_contact = db.Column(db.String(120))
    approved = db.Column(db.Boolean, default=False)
