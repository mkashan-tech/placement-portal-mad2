from flask import Blueprint, jsonify
from utils.decorators import role_required
from models.user import User
from models.company import Company
from models.job import JobPosition

admin_bp = Blueprint("admin", __name__)

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
    

