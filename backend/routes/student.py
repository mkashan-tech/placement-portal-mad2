from flask import Blueprint, jsonify, request, session 
from utils.decorators import role_required
from models.job import JobPosition
from models.application import Application 
from models.company import Company 
from extensions import db
from models.student import Student
from models.placement import Placement
from tasks.export_tasks import export_csv
from extensions import cache

student_bp = Blueprint("student", __name__)


@student_bp.route("/dashboard")
@role_required("student")
def student_dashbaord():
    return jsonify({"message": "Welcome Student"})


# View available jobs
@student_bp.route("/jobs")
@cache.cached(timeout=120, query_string=True)
@role_required("student")

def view_jobs():
    print("Fetching jobs from DB...")
    search = request.args.get("q")

    query = db.session.query(JobPosition)\
        .join(Company, JobPosition.company_id == Company.id)\
        .filter(
            JobPosition.status == "Active",
            JobPosition.approved == True,
            Company.approved == True
        )

    if search:
        query = query.filter(
            JobPosition.title.contains(search) |
            JobPosition.skills_required.contains(search)
        )

    jobs = query.all()

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
    if not student:
        return jsonify({"message": "Student profile not found"}), 404

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
    student = Student.query.filter_by(user_id=session["user_id"]).first()
    if not student:
        return jsonify({"message": "Student profile not found"}), 404

    applications = Application.query.filter_by(student_id=student.id).all()

    result = []

    for app in applications:
        job = JobPosition.query.get(app.drive_id)
        company = Company.query.get(job.company_id)

        result.append({
            "job_title": job.title,
            "company": company.company_name,
            "status": app.status,
            "interview_date": app.interview_date,
            "feedback": app.feedback,
            "applied_on": app.applied_on
        })

    return jsonify(result)


# Can Update their profile
@student_bp.route("/update-profile", methods=["PUT"])
@role_required("student")
def update_profile():
    student = Student.query.filter_by(user_id=session["user_id"]).first()

    if not student:
        return jsonify({"message": "Student not found"}), 404
    
    data = request.json

    student.name = data.get("name", student.name)
    student.branch = data.get("branch", student.branch)
    student.cgpa = data.get("cgpa", student.cgpa)
    student.skills = data.get("skills", student.skills)
    student.experience = data.get("experience", student.experience)
    student.education = data.get("education", student.education)

    db.session.commit()

    return jsonify({"message": "Profile updated successfully"})



# Can downlaod offerlette
@student_bp.route("/my-placements")
@role_required("student")
def my_placements():
    student = Student.query.filter_by(user_id=session["user_id"]).first()
    if not student:
        return jsonify({"message": "Student profile not found"}), 404
    placements = Placement.query.filter_by(student_id=student.id).all()
    
    result = []

    for p in placements:
        company = Company.query.get(p.company_id)
        result.append({
            "company_id": p.company_id,
            "company_name": company.company_name,
            "position": p.position,
            "salary": p.salary,
            "joining_date": p.joining_date
        })
    
    return jsonify(result)

# Basic downloadble offer lerter
@student_bp.route("/offer-letter/<int:placement_id>")
@role_required("student")
def offer_letter(placement_id):
    placement = Placement.query.get(placement_id)

    if not placement:
        return jsonify({"message": "Placement not found"}), 404
    
    return jsonify({
        "message": "Offer letter",
        "position": placement.position,
        "salary": placement.salary,
        "joining_date": placement.joining_date
    })


# ==============================
# Celery Work
# ==============================
@student_bp.route("/export")
@role_required("student")
def export_applications():
    student = Student.query.filter_by(user_id=session["user_id"]).first()
    applications = Application.query.filter_by(student_id=student.id).all()
    data = []

    for app in applications:
        job = JobPosition.query.get(app.drive_id)
        data.append([job.title, app.status, str(app.applied_on)])

    task = export_csv.delay(data, "student_export.csv")
    return jsonify({"message": "Export started", "task_id": task.id})
