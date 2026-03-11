from flask import Blueprint, jsonify, request
from utils.decorators import role_required
from models.user import User
from models.company import Company
from models.job import JobPosition
from models.company import Company
from extensions import db
from models.application import Application
from models.student import Student
from extensions import cache
from models.placement import Placement


admin_bp = Blueprint("admin", __name__)

# Dashboard
@admin_bp.route("/dashboard")
@role_required("admin")
@cache.cached(timeout=60)
def admin_dashboard():
    total_students = User.query.filter_by(role="student").count()
    total_companies = User.query.filter_by(role="company").count()
    total_jobs = JobPosition.query.count()
    total_applications = Application.query.count()

    return jsonify({
        "total_students": total_students,
        "total_companies": total_companies,
        "total_jobs": total_jobs,
        "total_applications": total_applications
    })


# Pending Companies
@admin_bp.route("/pending-companies")
def pending_companies():
    companies = Company.query.filter_by(approved=False).all()  
    result = []
    for c in companies:
        user = User.query.get(c.user_id)
        result.append({
            "id": c.id,
            "company_name": c.company_name,
            "email": user.email if user else "",
            "hr_contact": c.hr_contact
        })
    return jsonify(result)


# Approve Company
@admin_bp.route("/approve-company/<int:company_id>", methods=["PUT"])
@role_required("admin")
def approve_company(company_id):
    company = Company.query.get(company_id)

    if not company:
        return jsonify({"message": "Company not found"}), 404

    company.approved = True
    db.session.commit()

    return jsonify({"message": "Company approved"})

# Reject / Deactivate company
@admin_bp.route("/deactivate-company/<int:company_id>", methods=["PUT"])
@role_required('admin')
def deactivate_company(company_id):
    company = Company.query.get(company_id)

    if not company:
        return jsonify({"message": "Company not found"}), 404
    
    company.approved = False
    db.session.commit()

    return jsonify({"message": "Company deactivated"})




# Search Students
@admin_bp.route("/search-students")
@role_required('admin')
def search_students():
    from models.student import Student
    query = request.args.get("q")

    students = Student.query.filter(Student.name.contains(query)).all()

    result = []
    for s in students:
        result.append({
            "id": s.id,
            "name": s.name,
            "branch": s.branch
        })

    return jsonify(result)




# Pending Jobs
@admin_bp.route("/pending-jobs")
@role_required("admin")
def pending_jobs():
    jobs = JobPosition.query.filter_by(approved=False).all()
    return jsonify([{"id": j.id, "title": j.title} for j in jobs])



# View All Jobs (Approved and Pending both)
@admin_bp.route("/all-jobs")
@role_required("admin")
def view_all_jobs():
    from models.company import Company 
    jobs = JobPosition.query.all()
    
    result = []
    for j in jobs:
        company = Company.query.get(j.company_id)
        result.append({
            "id": j.id,
            "title": j.title,
            "company_name": company.company_name if company else "Unknown",
            "status": j.status,
            "approved": j.approved
        })
    return jsonify(result)
    
# Approve job
@admin_bp.route("/approve-job/<int:job_id>", methods=["PUT"])
@role_required("admin")
def approve_job(job_id):

    job = JobPosition.query.get(job_id)

    if not job:
        return jsonify({"message": "Job not found"}), 404

    job.approved = True
    job.status = "Active"
    db.session.commit()

    return jsonify({"message": "Job approved successfully"})

# Rejct job
@admin_bp.route("/reject-job/<int:job_id>", methods=["PUT"])
@role_required("admin")
def reject_job(job_id):

    job = JobPosition.query.get(job_id)

    if not job:
        return jsonify({"message": "Job not found"}), 404

    job.approved = False
    db.session.commit()

    return jsonify({"message": "Job rejected successfully"})

# Reopen job
@admin_bp.route("/reopen-drive/<int:job_id>", methods=["PUT"])
@role_required("admin")
def reopen_drive(job_id):
    job = JobPosition.query.get(job_id)
    if job:
        job.status = "Active"
        db.session.commit()
    return jsonify({"message": "Drive reopened"})


# Admin can view students profiles and applications
@admin_bp.route("/students-application/<int:student_id>")
@role_required("admin")
def view_student_applications(student_id):

    applications = Application.query.filter_by(student_id=student_id).all()

    result = []

    for a in applications:
        job = JobPosition.query.get(a.drive_id)

        result.append({
            "job_title": job.title,
            "status": a.status,
            "applied_on": a.applied_on

        })
    return jsonify(result)



# Admin can view all students
@admin_bp.route("/students")
#@cache.cached(timeout=180)
@role_required("admin")
def view_all_students():
    students = Student.query.all()
    result = []
    
    for s in students:
        # User table se is_active uthana padega kyunki status wahan hai
        user = User.query.get(s.user_id)
        # Sahi student_id ke liye applications count 
        app_count = Application.query.filter_by(student_id=s.id).count()
        
        result.append({
            "id": s.id,
            "name": s.name or "N/A",
            "branch": s.branch or "N/A",
            "cgpa": s.cgpa or 0,
            "is_active": user.is_active if user else True, # Frontend status ke liye
            "app_count": app_count # "View(n)" dikhane ke liye
        })
    return jsonify(result)


# Admin can view specifc student profile
@admin_bp.route("/student-profile/<int:student_id>")
@role_required("admin")
def admin_view_student_profile(student_id):
    
    student = Student.query.get(student_id)
    user = User.query.get(student.user_id)
    if not student:
        return jsonify({"message": "Student not found"}), 404
    
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


# Filter student by job applied
@admin_bp.route('/job-applicants/<int:job_id>')
@role_required("admin")
def job_applicants(job_id):

    applications = Application.query.filter_by(drive_id=job_id).all()

    result = []

    for a in applications:
        student = Student.query.get(a.student_id)

        result.append({
            "student_id": student.id,
            "name": student.name,
            "branch": student.branch,
            "status": a.status
        })

    return jsonify(result)

# More advanced filter
@admin_bp.route("/students/filter")
@role_required("admin")
def filter_students():

    branch = request.args.get("branch")
    min_cgpa = request.args.get("cgpa")

    query = Student.query

    if branch:
        query = query.filter(Student.branch == branch)

    if min_cgpa:
        query = query.filter(Student.cgpa >= float(min_cgpa))

    students = query.all()
    result = []
    for s in students:
        result.append({
            "id": s.id,
            "name": s.name,
            "branch": s.branch,
            "cgpa": s.cgpa
        })
    return jsonify(result)

# ==========================================
# ADMIN ADVANCED ROUTES
# ==========================================

from models.job import JobPosition
from models.company import Company
from models.user import User
from extensions import db
from flask import jsonify, request


# -------------------------------
# 1. View ALL Companies
# -------------------------------
@admin_bp.route("/all-companies")
@role_required("admin")
def all_companies():
    companies = Company.query.all()
    result = []

    for c in companies:
        user = User.query.get(c.user_id)
        result.append({
            "id": c.id,
            "company_name": c.company_name,
            "approved": c.approved,
            "active": user.is_active if user else True
        })

    return jsonify(result)


# -------------------------------
# 2. Search Companies
# -------------------------------
@admin_bp.route("/search-companies")
@role_required("admin")
def search_companies():
    q = request.args.get("q", "")

    companies = Company.query.filter(
        Company.company_name.contains(q)
    ).all()

    result = []
    for c in companies:
        user = User.query.get(c.user_id)
        result.append({
            "id": c.id,
            "company_name": c.company_name,
            "approved": c.approved,
            "active": user.is_active if user else True
        })

    return jsonify(result)





# -------------------------------
# 4. Toggle Student Active Status
# -------------------------------
@admin_bp.route("/toggle-student/<int:student_id>", methods=["PUT"])
@role_required("admin")
def toggle_student_status(student_id):
    from models.student import Student
    from models.user import User

    # 1. Student integer id ke sath
    student = Student.query.get(student_id)
    if not student:
        return jsonify({"message": "Student record not found"}), 404

    # 2. Linked User dhundo
    user = User.query.get(student.user_id)
    if not user:
        return jsonify({"message": "User account not found"}), 404

    # Agar is_active True hai toh False hoga, False hai toh True hoga
    user.is_active = not user.is_active
    db.session.commit()

    # Response mein naya status bhejein taaki confirm ho sake
    status_text = "activated" if user.is_active else "deactivated"
    return jsonify({
        "message": f"Student {status_text} successfully",
        "current_status": user.is_active
    }), 200


# =========== Monthly report============
@admin_bp.route("/trigger-report", methods=["POST"])
@role_required("admin")
def trigger_report():
    from tasks.report_tasks import generate_monthly_report
    generate_monthly_report.delay() # Simple Celery trigger
    return jsonify({"message": "Background task started"}), 202

@admin_bp.route("/view-report")
@role_required("admin")
def view_report():
    import os
    from flask import send_file
    files = [f for f in os.listdir("reports") if f.endswith('.html')]
    if not files: return "No report found", 404
    latest = max(files, key=lambda f: os.path.getctime(os.path.join("reports", f)))
    return send_file(os.path.join("reports", latest))



# Adding to admin.py - New endpoints
@admin_bp.route("/companies")
@role_required("admin")
def get_companies_list():
    companies = Company.query.all()
    result = []
    for c in companies:
        user = User.query.get(c.user_id)
        jobs_count = JobPosition.query.filter_by(company_id=c.id).count()
        result.append({
            "id": c.id,
            "company_name": c.company_name,
            "hr_contact": c.hr_contact,
            "approved": c.approved,
            "is_active": user.is_active if user else True,
            "jobs_count": jobs_count
        })
    return jsonify(result)

@admin_bp.route("/drives")
@role_required("admin")
def get_drives_list():
    jobs = JobPosition.query.all()
    result = []
    for j in jobs:
        company = Company.query.get(j.company_id)
        applicants_count = Application.query.filter_by(drive_id=j.id).count()
        result.append({
            "id": j.id,
            "company": company.company_name if company else "Unknown",
            "title": j.title,
            "salary": j.salary,
            "approved": j.approved,
            "status": j.status,
            "applicants_count": applicants_count
        })
    return jsonify(result)


@admin_bp.route("/toggle-company/<int:company_id>", methods=["PUT"])
@role_required("admin")
def toggle_company_status(company_id):
    company = Company.query.get(company_id)
    if not company:
        return jsonify({"message": "Company not found"}), 404
    
    user = User.query.get(company.user_id)
    user.is_active = not user.is_active
    db.session.commit()
    
    return jsonify({"message": "Company status updated"})

@admin_bp.route("/close-drive/<int:job_id>", methods=["PUT"])
@role_required("admin")
def close_drive_admin(job_id):
    job = JobPosition.query.get(job_id)
    if job:
        job.status = "Closed"
        db.session.commit()
    return jsonify({"message": "Drive closed"})

@admin_bp.route("/company-jobs/<int:company_id>")
@role_required("admin")
def get_company_jobs_admin(company_id):
    jobs = JobPosition.query.filter_by(company_id=company_id).all()
    result = []
    for j in jobs:
        applicants_count = Application.query.filter_by(drive_id=j.id).count()
        result.append({
            "id": j.id,
            "title": j.title,
            "status": j.status,
            "applicants_count": applicants_count
        })
    return jsonify(result)

