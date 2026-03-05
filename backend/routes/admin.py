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


admin_bp = Blueprint("admin", __name__)

# Dashboard
@admin_bp.route("/dashboard")
@role_required("admin")
@cache.cached(timeout=60)
def admin_dashboard():
    total_students = User.query.filter_by(role="student").count()
    total_companies = User.query.filter_by(role="company").count()
    total_jobs = JobPosition.query.count()

    return jsonify({
        "total_students": total_students,
        "total_companies": total_companies,
        "total_jobs": total_jobs
    })

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
    
    company.deactivate = True
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

# Deactivate Students
@admin_bp.route("/deactivate-student/<student_id>", methods=["PUT"])
@role_required("admin")
def deactivate_user(student_id):
    
    student = Student.query.get(student_id)
    user = User.query.get(student.user_id)

    if not student:
        return jsonify({"message": "Student not found"}), 404
    
    user.is_active = False
    db.session.commit()

    return jsonify({"message": "Student deactivated"}), 200

    
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
@cache.cached(timeout=180)
@role_required("admin")
def view_all_students():

    students = Student.query.all()
    result = []
    
    for s in students:
        result.append({
            "id": s.id,
            "name": s.name,
            "branch": s.branch,
            "cgpa": s.cgpa
        })
    return jsonify(result)


# Admin can view specifc student profile
@admin_bp.route("/student-profile/<int:student_id>")
@role_required("admin")
def admin_view_student_profile(student_id):
    
    student = Student.query.get(student_id)
    if not student:
        return jsonify({"message": "Student not found"}), 404
    
    return jsonify({
        "name": student.name,
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