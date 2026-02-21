from flask import Blueprint, jsonify, request
from utils.decorators import role_required
from models.user import User
from models.company import Company
from models.job import JobPosition
from models.company import Company
from models.db import db

admin_bp = Blueprint("admin", __name__)

# Dashboard
@admin_bp.route("/dashboard")
@role_required("admin")
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
    company = Company.query.get('company_id')

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
@admin_bp.route("/deactivate-user/<int:user_id>", methods=["PUT"])
@role_required('admin')
def deactivate_user(user_id):
    from models.user import User

    user = User.query.get(user_id)

    if not user:
        return jsonify({"message": "User not found"}), 404
    
    user.is_active = False
    db.session.commit()

    return jsonify({"message": "User deactivated"}), 403

    

