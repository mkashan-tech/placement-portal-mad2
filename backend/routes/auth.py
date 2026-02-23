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

    email = data.get("email")
    password = data.get("password")
    company_name = data.get("company_name")
    hr_contact = data.get("hr_contact", "")

    # Required fields validation
    if not email or not password or not company_name:
        return jsonify({"message": "Email, password and company name are required"}), 400

    # HR contact validation (exactly 10 digits)
    if not re.fullmatch(r"\d{10}", hr_contact):
        return jsonify({"message": "HR contact must be exactly 10 digits"}), 400

    # Duplicate email check
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"message": "Email already registered"}), 409

    try:
        # Create user
        user = User(
            email=email,
            password=password,
            role="company"
        )
        db.session.add(user)
        db.session.commit()

        # Create company profile
        company = Company(
            user_id=user.id,
            company_name=company_name,
            website=data.get("website", ""),
            hr_contact=hr_contact,
            approved=False
        )

        db.session.add(company)
        db.session.commit()

        return jsonify({"message": "Company registered successfully. Awaiting admin approval"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Registration failed", "error": str(e)}), 500

# Common login for all
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    
    # 1. Safety check for missing keys
    email = data.get("email")
    password = data.get("password")
    
    if not email or not password:
        return jsonify({"message": "Email and password are required"}), 400

    user = User.query.filter_by(email=email).first()

    # 2. Check credentials before setting session
    if user and user.password == password:
        
        if not user.is_active:
            return jsonify({"message": "Account deactivated"}), 403
        
        # 3. Role-based approval Check (Specifically for Companies)
        if user.role == "company":
            from models.company import Company
            company = Company.query.filter_by(user_id=user.id).first()
            
            # Check if company exists and is approved
            if not company or not company.approved:
                return jsonify({"message": "Company not approved by admin"}), 403

        # 4. Set session only after all checks pass
        session["user_id"] = user.id
        session["role"] = user.role
        
        return jsonify({"message": "Login success", "role": user.role})
    
    return jsonify({"message": "Invalid credentials"}), 401


# Logout
@auth_bp.route("/logout")
def logout():
    session.clear()
    return jsonify({"message": "Logged out"})