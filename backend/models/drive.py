from extensions import db

class PlacementDrive(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("company.id"))
    job_title = db.Column(db.String(120))
    description = db.Column(db.Text)
    eligibility = db.Column(db.String(120))
    deadline = db.Column(db.DateTime)
    status = db.Column(db.String(20))
