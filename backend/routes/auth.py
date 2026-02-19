from flask import Blueprint, session, request, jsonify
from models.user import User
from models.db import db

auth_bp = Blueprint("auth",__name__)

# Student Registration
@auth_bp.route("/register/student", methods=["POST"])
def register_student():
    data = request.json

    existing_user = User.query.filter_by(email=data["email"]).first()
    if existing_user:
        return jsonify({"message": "Email already registered"}), 400

    user = User(
        email=data["email"],
        password=data["password"],
        role="student"
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "Student registered succesfully!"})


# Company Registration
@auth_bp.route("/register/company", methods=["POST"])
def register_company():
    from models.company import Company
    import re

    data = request.json
    hr_contact = data.get("hr_contact", "")

    # Validation: Must be exactly 10 digits
    if not re.fullmatch(r"\d{10}", hr_contact):
        return jsonify({"message": "HR contact must be exactly 10 digits."}), 400

    user = User(
        email=data["email"],
        password=data["password"],
        role="company"
    )
    db.session.add(user)
    db.session.commit()

    company = Company(
        user_id=user.id,
        company_name=data["company_name"],
        website=data.get("website", ""),
        hr_contact=hr_contact,
        approved=False
    )

    db.session.add(company)
    db.session.commit()

    return jsonify({"message": "Company registered. Waiting for admin approval"})


# Common login for all
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json

    user = User.query.filter_by(email=data["email"]).first()

    if user and user.password == data["password"]:
        session["user_id"] = user.id
        session["role"] = user.role
        
        return jsonify({"message": "Login success", "role": user.role})
    return jsonify({"message": "Invalid credentials"}), 401


# Logout
@auth_bp.route("/logout")
def logout():
    session.clear()
    return jsonify({"message": "Logged out"})