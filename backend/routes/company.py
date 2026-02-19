from flask import Blueprint, jsonify
from utils.decorators import role_required

company_bp = Blueprint("company", __name__)

@company_bp.route("/dashboard")
@role_required("company")
def company_dashboard():
    return jsonify({"message": "Welcome Company"})