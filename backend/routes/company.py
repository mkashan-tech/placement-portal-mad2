from flask import Blueprint, jsonify, request, session
from models.job import JobPosition
from models.company import Company
from utils.decorators import role_required
from models.db import db
from models.application import Application
from models.student import Student

company_bp = Blueprint("company", __name__)

# Company dashboard
@company_bp.route("/dashboard")
@role_required("company")
def company_dashboard():
    company = Company.query.filter_by(user_id=session["user_id"]).first()

    if not company:
        return jsonify({"message": "Company not found"}), 404

    # total jobs
    total_jobs = JobPosition.query.filter_by(company_id=company.id).count()

    # total active jobs
    active_jobs = JobPosition.query.filter_by(
        company_id=company.id,
        status="Active"
    ).count()

    # total applications (join query)
    total_applications = db.session.query(Application)\
        .join(JobPosition, Application.drive_id == JobPosition.id)\
        .filter(JobPosition.company_id == company.id)\
        .count()

    # Shortlisted count
    shortlisted_count = db.session.query(Application)\
        .join(JobPosition, Application.drive_id == JobPosition.id)\
        .filter(
            JobPosition.company_id == company.id,
            Application.status == "Shortlisted"
        ).count()

    return jsonify({
        "total_jobs": total_jobs,
        "active_jobs": active_jobs,
        "total_applications": total_applications,
        "shortlisted_count": shortlisted_count
    })




# Create Jobs
@company_bp.route("/create-job", methods=['POST'])
@role_required("company")
def create_job():
    data = request.json 

    company = Company.query.filter_by(user_id=session["user_id"]).first()

    job = JobPosition(
        company_id=company.id,
        title = data.get("title"),
        description = data.get("description"),
        salary = data.get("salary"),
        skills_required = data.get("skills_required"),
        experience_required = data.get("experience_required"),
        benefits = data.get("benefits"),
        location = data.get("location"),
        status="Active"
    )
    db.session.add(job)
    db.session.commit()

    return jsonify({"message": "Job created successfully, waiting for admin approval"})


# View Own Jobs
@company_bp.route("/view-jobs")
@role_required("company")
def view_jobs():
    company = Company.query.filter_by(user_id=session["user_id"]).first()
    jobs = JobPosition.query.filter_by(company_id=company.id).all()

    result = []
    for j in jobs:
        result.append({
            "id": j.id,
            "title": j.title,
            "salary": j.salary,
            "status": j.status
        })

    return jsonify(result)


# Close job
@company_bp.route("/close-job/<int:job_id>", methods=["PUT"])
@role_required("company")
def close_job(job_id):

    company = Company.query.filter_by(user_id=session["user_id"]).first()

    job = JobPosition.query.filter_by(id=job_id, company_id=company.id).first()

    if not job:
        return jsonify({"message": "Unauthorized or job not found"}), 403

    job.status = "Closed"
    db.session.commit()

    return jsonify({"message": "Job closed"})


# View Applicants per job
@company_bp.route("/applicants/<int:job_id>")
@role_required("company")
def view_applicants(job_id):
    company = Company.query.filter_by(user_id=session["user_id"]).first()

    job = JobPosition.query.get(job_id)

    if not job or job.company_id != company.id:
        return jsonify({"message": "Unauthorized access"}), 403

    applications = Application.query.filter_by(drive_id=job_id).all()

    result = []

    for app in applications:
        student = Student.query.get(app.student_id)

        result.append({
            "application_id": app.id,
            "student_name": student.name,
            "branch": student.branch,
            "cgpa": student.cgpa,
            "status": app.status,
            "interview_date": app.interview_date
        })

    return jsonify(result)

# update applicatio status
@company_bp.route("/update-application/<int:app_id>", methods=["PUT"])
@role_required("company")
def update_application(app_id):

    company = Company.query.filter_by(user_id=session["user_id"]).first()
    application = Application.query.get(app_id)

    if not application:
        return jsonify({"message": "Application not found"}), 404

    job = JobPosition.query.get(application.drive_id)

    if not job or job.company_id != company.id:
        return jsonify({"message": "Unauthorized"}), 403

    data = request.json
    new_status = data.get("status")

    allowed_status = ["Applied", "Shortlisted", "Interview", "Selected", "Rejected"]

    # Validate status before updating
    if new_status and new_status not in allowed_status:
        return jsonify({"message": "Invalid status"}), 400

    # Update fields safely
    if new_status:
        application.status = new_status

    if data.get("interview_date"):
        application.interview_date = data.get("interview_date")

    if data.get("feedback"):
        application.feedback = data.get("feedback")

    # Create placement only if selected and not already placed
    if new_status == "Selected":
        from models.placement import Placement

        existing_placement = Placement.query.filter_by(
            student_id=application.student_id,
            company_id=company.id
        ).first()

        if not existing_placement:
            placement = Placement(
                student_id=application.student_id,
                company_id=company.id,
                position=job.title,
                salary=job.salary,
                joining_date=data.get("joining_date")
            )
            db.session.add(placement)

    db.session.commit()

    return jsonify({"message": "Application updated successfully"})