from flask import Blueprint, jsonify, request, session 
from utils.decorators import role_required
from models.job import JobPosition
from models.application import Application 
from models.company import Company 
from models.db import db 

student_bp = Blueprint("student", __name__)

student_bp = Blueprint("student", __name__)

@student_bp.route("/dashboard")
@role_required("student")
def student_dashbaord():
    return jsonify({"message": "Welcome Student"})


# View available jobs
@student_bp.route("/jobs")
@role_required("student")
def view_jobs():
    jobs = JobPosition.query.filter_by(status="Active").all()

    result = []

    for j in jobs:
        company = Company.query.get(j.company_id)

        result.append({
            "job_id": j.id,
            "title": j.title,
            "company": company.company_name,
            "salary": j.salary,
            "skills_required": j.skills_required

        })

    return jsonify(result)


# Apply for jobs
@student_bp.route("/apply/<int:job_id>", methods=["POST"])
@role_required("student")
def apply_job(job_id):
    from models.student import Student

    student = Student.query.filter_by(user_id=session["user_id"]).first()

    # Check if job exist and active
    job = JobPosition.query.get(job_id)

    if not job or job.status != "Active":
        return jsonify({"message": "Job not available"}), 400
    
    # Prevent duplicate application
    existing = Application.query.filter_by(
        student_id=student.id,
        drive_id = job_id
    ).first()

    if existing:
        return jsonify({"message": "Already applied"}), 400
    
    application = Application(
        student_id=student.id,
        drive_id=job_id,
        status="Applied"
    )
    db.session.add(application)
    db.session.commit()

    return jsonify({"message": "Application submitted"})


# Student View Application History
@student_bp.route("/my-applications")
@role_required("student")
def view_applications():
    from models.student import Student
    
    student = Student.query.filter_by(user_id=session["user_id"]).first()

    applications = Application.query.filter_by(student_id=student.id).all()

    result = []

    for app in applications:
        job = JobPosition.query.get(app.drive_id)

        result.append({
            "job_title": job.title,
            "status": app.status,
            "applied_on": app.applied_on
        })

    return jsonify(result)