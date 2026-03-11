from flask import Blueprint, jsonify, request, session
from models.job import JobPosition
from models.company import Company
from utils.decorators import role_required
from extensions import db
from models.application import Application
from models.student import Student
from extensions import cache
from datetime import datetime
from dateutil import parser   
from models.user import User

company_bp = Blueprint("company", __name__)

# ---------------- Company dashboard --------------------------------
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
        "is_approved": company.approved,
        "total_jobs": total_jobs,
        "active_jobs": active_jobs,
        "total_applications": total_applications,
        "shortlisted_count": shortlisted_count
    })




# ---------------------- Create Jobs ---------------------------------
@company_bp.route("/create-job", methods=['POST'])
@role_required("company")
def create_job():
    data = request.json 

    company = Company.query.filter_by(user_id=session["user_id"]).first()
    if not company:
        return jsonify({"message": "Company not found"}), 404
    if not company.approved:
        return jsonify({"message": "Company not approved"}), 403

    job = JobPosition(
        company_id=company.id,
        title = data.get("title"),
        description = data.get("description"),
        salary = data.get("salary"),
        skills_required = data.get("skills_required"),
        eligibility = data.get("eligibility"),
        experience_required = data.get("experience_required"),
        benefits = data.get("benefits"),
        location = data.get("location"),
        status="Pending",
        approved=False
    )
    db.session.add(job)
    db.session.commit()
    cache.delete_memoized(view_company_jobs)

    return jsonify({"message": "Job created successfully, waiting for admin approval"})


# ----------------------- View Own Jobs ------------------------------------------
@company_bp.route("/view-jobs")
@role_required("company")
def view_company_jobs():
    company = Company.query.filter_by(user_id=session["user_id"]).first()
    jobs = JobPosition.query.filter_by(company_id=company.id).all()

    result = []
    for j in jobs:
        
        applicants_count = Application.query.filter_by(drive_id=j.id).count()
        
        result.append({
            "id": j.id,
            "title": j.title,
            "salary": j.salary,
            "location": j.location,
            "status": j.status,
            "approved": j.approved,
            "applicants_count": applicants_count  
        })

    return jsonify({
        "jobs": result,
        "company_approved": company.approved
    })


# ------------------------ Close job ----------------------------------------
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


# ------------------------------ Reopen Job -----------------------------------------
@company_bp.route("/reopen-job/<int:job_id>", methods=["PUT"])
@role_required("company")
def reopen_job(job_id):
    company = Company.query.filter_by(user_id=session["user_id"]).first()
    job = JobPosition.query.filter_by(id=job_id, company_id=company.id).first()
    if not job:
        return jsonify({"message": "Unauthorized"}), 403
    job.status = "Active"
    db.session.commit()
    return jsonify({"message": "Job reopened"})

# ------------------------- View Applicants per job --------------------------------------
@company_bp.route("/applicants/<int:job_id>")
@role_required("company")
#@cache.cached(timeout=120, query_string=True)
def view_applicants(job_id):
    company = Company.query.filter_by(user_id=session["user_id"]).first()
    job = JobPosition.query.get(job_id)

    if not job or job.company_id != company.id:
        return jsonify({"message": "Unauthorized access"}), 403

    applications = Application.query.filter_by(drive_id=job_id).all()
    
    # total student count for this job
    total_applicants = len(applications)  # Ya .count()

    result = []
    for app in applications:
        student = Student.query.get(app.student_id)
        
        result.append({
            "application_id": app.id,
            "student_name": student.name,
            "student_id": student.id,
            "branch": student.branch,
            "cgpa": student.cgpa,
            "status": app.status,
            "interview_date": app.interview_date,
        
            # "applicants_count": total_applicants > Yeh har row mein same hoga
        })

    # count ko alag se bheja
    return jsonify({
        "applicants": result,
        "applicants_count": total_applicants
    })
from datetime import datetime
from models.placement import Placement

# ---------------------- Update Application status ----------------------------------
@company_bp.route("/update-application/<int:app_id>", methods=["PUT"])
@role_required("company")
def update_application(app_id):

    company = Company.query.filter_by(user_id=session["user_id"]).first()
    if not company:
        return jsonify({"message": "Company not found"}), 404

    application = Application.query.get(app_id)
    if not application:
        return jsonify({"message": "Application not found"}), 404

    job = JobPosition.query.get(application.drive_id)

    if not job or job.company_id != company.id:
        return jsonify({"message": "Unauthorized"}), 403

    data = request.json
    new_status = data.get("status")

    allowed_status = [
        "Applied",
        "Shortlisted",
        "Interview",
        "Selected",
        "Rejected",
        "Placed"
    ]

    if new_status and new_status not in allowed_status:
        return jsonify({"message": "Invalid status"}), 400

    valid_transitions = {
        "Applied": ["Shortlisted", "Rejected", "Interview"],
        "Shortlisted": ["Interview", "Rejected", "Selected"],
        "Interview": ["Selected", "Rejected", "Interview", "Shortlisted"],
        "Selected": ["Placed", "Rejected"],
        "Rejected": [],
        "Placed": []
    }

    current_status = application.status

    if new_status:
        if new_status not in valid_transitions.get(current_status, []):
            return jsonify({
                "message": f"Invalid transition from {current_status} to {new_status}"
            }), 400

        application.status = new_status

    # Interview Date Update
    if data.get("interview_date"):
        application.interview_date = parser.parse(data.get("interview_date"))
        
    # Feedback
    if data.get("feedback"):
        application.feedback = data.get("feedback")

    # Placement Creation
    if application.status == "Selected":

        existing_placement = Placement.query.filter_by(
            student_id=application.student_id,
            position=job.title,
            company_id=company.id
        ).first()

        if existing_placement:
            if data.get("joining_date"):
                existing_placement.joining_date = parser.parse(data.get("joining_date"))

        else:
            joining_date = None
            if data.get("joining_date"):
                joining_date = parser.parse(data.get("joining_date"))

            placement = Placement(
                student_id=application.student_id,
                company_id=company.id,
                position=job.title,
                salary=job.salary,
                joining_date=joining_date
            )
            db.session.add(placement)
        #Commit
        application.status = "Placed" 
        db.session.commit()

        return jsonify({"message": "Application updated successfully"})
    
    db.session.commit()
    return jsonify({"message": "Application updated successfully"})


# ------------ Company can view student profile which applied for job ----------------------------
@company_bp.route("/student-profile/<int:student_id>/<int:job_id>")
@role_required("company")
def view_student_profile(student_id, job_id):

    company = Company.query.filter_by(user_id=session['user_id']).first()

    # Chekc job belong to thast company
    job = JobPosition.query.get(job_id)
    if not job or job.company_id != company.id:
        return jsonify({"message": "Unauthorized"}), 403
    
    # Check student applied to this job
    application = Application.query.filter_by(
        student_id=student_id,
        drive_id=job_id
    ).first()
    
    if not application:
        return jsonify({"message": "Student did not applied to this job"}), 403
    

    student = Student.query.get(student_id)
    user = User.query.get(student.user_id)

    return jsonify({
        "name": student.name,
        "email": user.email,
        "branch": student.branch,
        "cgpa": student.cgpa,
        "skills": student.skills,
        "experience": student.experience,
        "education": student.education,
        "resume": student.resume
    })


# ---------------- UPDATE JOB ------------------------------------------
@company_bp.route("/update-job/<int:job_id>", methods=["PUT"])
@role_required("company")
def update_job(job_id):
    company = Company.query.filter_by(user_id=session["user_id"]).first()
    job = JobPosition.query.filter_by(id=job_id, company_id=company.id).first()
    if not job:
        return jsonify({"message":"Unauthorized"}),403

    data = request.json
    job.title = data.get("title", job.title)
    job.salary = data.get("salary", job.salary)
    job.skills_required = data.get("skills_required", job.skills_required)
    job.location = data.get("location", job.location)
    job.description = data.get("description", job.description)

    db.session.commit()
    return jsonify({"message":"Job updated"})
