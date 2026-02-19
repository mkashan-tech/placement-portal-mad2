from flask import Blueprint, jsonify
from utils.decorators import role_required

student_bp = Blueprint("student", __name__)

student_bp = Blueprint("student", __name__)

@student_bp.route("/dashboard")
@role_required("student")
def student_dashbaord():
    return jsonify({"message": "Welcome Student"})