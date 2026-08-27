from flask import Blueprint, jsonify, request, session, send_file, current_app
from utils.decorators import role_required
from models.job import JobPosition
from models.application import Application 
from models.company import Company 
from extensions import db
from models.student import Student
from models.placement import Placement
from tasks.export_tasks import export_csv
from extensions import cache
import os
from werkzeug.utils import secure_filename



student_bp = Blueprint("student", __name__)

# ---------- Dashboard ---------------------
@student_bp.route("/dashboard")
@role_required("student")
def student_dashboard():
    return jsonify({"message": "Welcome Student"})



# ---------- Apply for jobs ------------------------
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


# -------------- Student View Application History -------------------
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
            "application_id": app.id,
            "job_id": job.id,
            "job_title": job.title,
            "company": company.company_name,
            "status": app.status,
            "interview_date": app.interview_date,
            "feedback": app.feedback,
            "applied_on": app.applied_on
        })

    return jsonify(result)


# ------------------ Can Update their profile --------------------------
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




# =============================================
# Celery Work
# =============================================
# Export the data
@student_bp.route("/export")
@role_required("student")
def export_applications():
    student = Student.query.filter_by(user_id=session["user_id"]).first()
    if not student:
        return jsonify({"message": "Student not found"}), 404

    applications = Application.query.filter_by(student_id=student.id).all()
    data = []

    for app in applications:
        job = JobPosition.query.get(app.drive_id)
        company = Company.query.get(job.company_id) if job else None

        data.append([
            student.id,
            company.company_name if company else "Unknown",
            job.title if job else "Unknown",
            app.status,
            app.applied_on.strftime("%d-%m-%Y") if app.applied_on else "",
            app.interview_date.strftime("%d-%m-%Y %H:%M") if app.interview_date else ""
        ])

    task = export_csv.delay(data, "student_export.csv")

    return jsonify({
        "message": "Export started",
        "task_id": task.id
    })


# ------------------- Download csv ------------------------
@student_bp.route("/download-export")
@role_required("student")
def download_export():
    filepath = os.path.join("exports", "student_export.csv")

    if not os.path.exists(filepath):
        return jsonify({"message": "File not ready yet"}), 404

    return send_file(filepath, as_attachment=True)

# =========================================================
# STUDENT ADVANCED FEATURES 
# ======================================================

# --------------------------------------------------
# 2. UPLOAD RESUME
# --------------------------------------------------
@student_bp.route("/upload-resume", methods=["POST"])
@role_required("student")
def upload_resume():

    if "resume" not in request.files:
        return jsonify({"message": "No file uploaded"}), 400

    file = request.files["resume"]

    if file.filename == "":
        return jsonify({"message": "Empty filename"}), 400

    filename = secure_filename(file.filename)

    upload_folder = os.path.join(current_app.root_path, "uploads")
    os.makedirs(upload_folder, exist_ok=True)

    filepath = os.path.join(upload_folder, filename)
    file.save(filepath)

    student = Student.query.filter_by(user_id=session["user_id"]).first()
    student.resume = f"/api/student/resume-file/{filename}"
    db.session.commit()

    return jsonify({
        "message": "Resume uploaded successfully",
        "resume_url": student.resume
    })


# --------------------------------------------------
# 3. SERVE RESUME FILE
# --------------------------------------------------
@student_bp.route("/resume-file/<filename>")
def serve_resume(filename):
    # Viewed by the student themselves, or by an admin/company reviewing
    # a profile — so we only require *some* logged-in session here,
    # not a specific role.
    if "role" not in session:
        return jsonify({"message": "Unauthorized"}), 401

    upload_folder = os.path.join(current_app.root_path, "uploads")
    filepath = os.path.join(upload_folder, secure_filename(filename))
    if not os.path.exists(filepath):
        return jsonify({"message": "File not found"}), 404

    return send_file(filepath, as_attachment=True)


# --------------------------------------------------
# 4. ADVANCED JOB SEARCH & FILTERS
# --------------------------------------------------
@student_bp.route("/jobs")
@role_required("student")
def advanced_jobs():

    search = request.args.get("q", "")
    skill = request.args.get("skill", "")
    salary = request.args.get("salary", type=int)

    query = db.session.query(JobPosition)\
        .join(Company, JobPosition.company_id == Company.id)\
        .filter(
            JobPosition.status == "Active",
            JobPosition.approved == True,
            Company.approved == True
        )

    if search:
        query = query.filter(JobPosition.title.contains(search))

    if skill:
        query = query.filter(JobPosition.skills_required.contains(skill))

    if salary:
        query = query.filter(JobPosition.salary >= salary)

    jobs = query.all()

    result = []
    for j in jobs:
        company = Company.query.get(j.company_id)
        result.append({
            "job_id": j.id,
            "title": j.title,
            "eligibility": j.eligibility,
            "location": j.location,
            "company": company.company_name if company else "Unknown",
            "salary": j.salary,
            "skills_required": j.skills_required
        })

    return jsonify(result)

# ===========Placement Record===============
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
            "joining_date": p.joining_date,
            "placement_id": p.id
        })
   
    return jsonify(result)


# --------------------------------------------------
# 5. OFFER LETTER — HTML VIEW
# --------------------------------------------------
@student_bp.route("/offer-letter-html/<int:placement_id>")
@role_required("student")
def offer_letter_html(placement_id):

    placement = Placement.query.get(placement_id)
    if not placement:
        return "Placement not found", 404

    student = Student.query.filter_by(user_id=session["user_id"]).first()
    if placement.student_id != student.id:
        return "Unauthorized", 403

    company = Company.query.get(placement.company_id)

    html = f"""
    <html>
    <head>
        <title>Offer Letter</title>
        <style>
            body {{ font-family: Arial; padding:40px; background:#f5f5f5; }}
            .box {{ background:white; border:1px solid #ccc; padding:30px; }}
            h1 {{ text-align:center; }}
        </style>
    </head>
    <body>
        <div class="box">
            <h1>Offer Letter</h1>

            <p>Date: {placement.joining_date.strftime("%d-%m-%Y")}</p>

            <p>Dear <b>{student.name}</b>,</p>

            <p>
            We are pleased to offer you the position of
            <b>{placement.position}</b> at
            <b>{company.company_name}</b>.
            </p>

            <p><b>Salary:</b> ₹ {placement.salary} LPA</p>
            <p><b>Joining Date:</b> {placement.joining_date.strftime("%d-%m-%Y")}</p>

            <br><br>
            <p>Congratulations and welcome to the team!</p>

            <br><br>
            <p>
            <b>HR Department</b><br>
            {company.company_name}
            </p>
        </div>
    </body>
    </html>
    """

    return html


# ---------------- profile -------------------------------------
@student_bp.route("/profile")
@role_required("student")
def get_student_profile():
    student = Student.query.filter_by(user_id=session["user_id"]).first()
    if not student:
        return jsonify({})
    
    return jsonify({
        "name": student.name,
        "branch": student.branch,
        "cgpa": student.cgpa,
        "skills": student.skills,
        "education": student.education,
        "experience": student.experience,
        "resume": student.resume
    })