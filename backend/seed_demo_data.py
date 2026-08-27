"""
seed_demo_data.py

Quick script to populate the DB with realistic-looking sample data —
a few companies, students, jobs, and applications spanning every
status (Applied, Shortlisted, Interview, Rejected, Placed). Useful
for local testing so the dashboards aren't empty.

Run from backend/:
    python seed_demo_data.py

Safe to re-run — skips anything that already exists (matched by email).
"""

from datetime import datetime, timedelta
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app import app
from extensions import db
from models.user import User
from models.student import Student
from models.company import Company
from models.job import JobPosition
from models.application import Application
from models.placement import Placement


def get_or_create_user(email, password, role):
    user = User.query.filter_by(email=email).first()
    if user:
        return user
    user = User(email=email, role=role, is_active=True)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user


def seed():
    with app.app_context():
        db.create_all()

        # ---------------- Companies ----------------
        companies_data = [
            # (email, password, name, hr_contact, website, approved)
            ("hr@techsphere.com",    "pass123", "TechSphere Solutions", "9876500001", "techsphere.com",    True),
            ("careers@finedge.com",  "pass123", "FinEdge Analytics",    "9876500002", "finedge.com",       True),
            ("hr@cloudnova.io",      "pass123", "CloudNova Systems",    "9876500003", "cloudnova.io",      True),
            ("hiring@brightgrid.com","pass123", "BrightGrid Energy",    "9876500004", "brightgrid.com",    False),  # kept pending on purpose
        ]
        companies = {}
        for email, pwd, name, hr, site, approved in companies_data:
            user = get_or_create_user(email, pwd, "company")
            company = Company.query.filter_by(user_id=user.id).first()
            if not company:
                company = Company(
                    user_id=user.id, company_name=name, website=site,
                    hr_contact=hr, approved=approved
                )
                db.session.add(company)
                db.session.commit()
            companies[name] = company

        # ---------------- Students ----------------
        students_data = [
            ("aarav.sharma@univ.edu", "Aarav Sharma", "CSE", 8.7,
             "Python, React, SQL, Data Structures",
             "Built a food-delivery app during a college hackathon; 2-month backend internship at a startup.",
             "B.Tech Computer Science, XYZ Institute of Technology, 2022-2026"),
            ("diya.patel@univ.edu", "Diya Patel", "ECE", 9.1,
             "Embedded C, VLSI, IoT, MATLAB",
             "Published a paper on low-power IoT sensor networks; college robotics club lead.",
             "B.Tech Electronics & Communication, XYZ Institute of Technology, 2022-2026"),
            ("rohan.mehta@univ.edu", "Rohan Mehta", "CSE", 7.9,
             "Java, Spring Boot, Docker, AWS",
             "Freelance backend work for 2 small businesses; open-source contributor.",
             "B.Tech Computer Science, XYZ Institute of Technology, 2022-2026"),
            ("sneha.iyer@univ.edu", "Sneha Iyer", "CE", 8.3,
             "JavaScript, Node.js, MongoDB, System Design",
             "Teaching assistant for Web Development course; built 3 full-stack side projects.",
             "B.Tech Computer Engineering, XYZ Institute of Technology, 2022-2026"),
            ("kabir.singh@univ.edu", "Kabir Singh", "ME", 7.5,
             "AutoCAD, SolidWorks, Thermodynamics",
             "Summer internship at an automotive parts manufacturer.",
             "B.Tech Mechanical Engineering, XYZ Institute of Technology, 2022-2026"),
            ("ananya.rao@univ.edu", "Ananya Rao", "CSE", 9.4,
             "Python, Machine Learning, TensorFlow, Pandas",
             "Research intern at a university AI lab; 2x Kaggle competition top-10 finish.",
             "B.Tech Computer Science, XYZ Institute of Technology, 2022-2026"),
        ]
        students = {}
        for email, name, branch, cgpa, skills, exp, edu in students_data:
            user = get_or_create_user(email, "pass123", "student")
            student = Student.query.filter_by(user_id=user.id).first()
            if not student:
                student = Student(user_id=user.id, name=name, branch=branch, cgpa=cgpa,
                                   skills=skills, experience=exp, education=edu, resume="")
                db.session.add(student)
                db.session.commit()
            else:
                # fill in profile in case it was created blank by registration
                student.name, student.branch, student.cgpa = name, branch, cgpa
                student.skills, student.experience, student.education = skills, exp, edu
                db.session.commit()
            students[name] = student

        # ---------------- Jobs ----------------
        jobs_data = [
            # (company, title, salary, skills, eligibility, exp_req, benefits, location, status, approved)
            ("TechSphere Solutions", "Software Development Engineer", 12,
             "Python, React, SQL", "CGPA >= 7.5", "0-1 years",
             "Health insurance, WFH flexibility, annual bonus", "Bengaluru", "Active", True),
            ("FinEdge Analytics", "Data Analyst", 9.5,
             "SQL, Python, Power BI", "CGPA >= 7.0", "0-2 years",
             "Health insurance, learning stipend", "Mumbai", "Active", True),
            ("CloudNova Systems", "Cloud Support Engineer", 10.5,
             "AWS, Docker, Linux", "CGPA >= 7.0", "0-1 years",
             "Cloud certification sponsorship, relocation assistance", "Pune", "Active", True),
            ("TechSphere Solutions", "QA Automation Intern", 6,
             "Selenium, Java, Testing", "CGPA >= 6.5", "0 years",
             "Pre-placement offer for top performers", "Bengaluru", "Closed", True),
            ("FinEdge Analytics", "ML Research Intern", 8,
             "Python, TensorFlow, Statistics", "CGPA >= 8.0", "0 years",
             "Mentorship from senior data scientists", "Mumbai", "Pending", False),  # awaiting admin approval
        ]
        jobs = {}
        for cname, title, salary, skills, elig, exp_req, benefits, loc, status, approved in jobs_data:
            company = companies[cname]
            job = JobPosition.query.filter_by(company_id=company.id, title=title).first()
            if not job:
                job = JobPosition(
                    company_id=company.id, title=title, salary=salary,
                    skills_required=skills, description=f"Exciting {title} role at {cname}.",
                    location=loc, experience_required=exp_req, benefits=benefits,
                    eligibility=elig, status=status, approved=approved,
                    created_at=datetime.utcnow()
                )
                db.session.add(job)
                db.session.commit()
            jobs[title] = job

        # ---------------- Applications (spread across every status) ----------------
        apps_data = [
            # (student, job, status, interview_date_offset_days, feedback)
            ("Aarav Sharma", "Software Development Engineer", "Placed", None, "Strong technical round, great fit."),
            ("Ananya Rao", "ML Research Intern", "Applied", None, None),  # job itself pending, will just sit as Applied
            ("Diya Patel", "Cloud Support Engineer", "Interview", 3, None),
            ("Rohan Mehta", "Software Development Engineer", "Shortlisted", None, None),
            ("Sneha Iyer", "Data Analyst", "Interview", 5, "Good communication, awaiting final round."),
            ("Kabir Singh", "QA Automation Intern", "Rejected", None, "Skill set not aligned with current opening."),
            ("Ananya Rao", "Data Analyst", "Placed", None, "Excellent analytical skills, offer extended."),
        ]

        for sname, jtitle, status, interview_offset, feedback in apps_data:
            student = students[sname]
            job = jobs.get(jtitle)
            if not job:
                continue
            existing = Application.query.filter_by(student_id=student.id, drive_id=job.id).first()
            if existing:
                continue
            interview_date = (datetime.utcnow() + timedelta(days=interview_offset)) if interview_offset else None
            application = Application(
                student_id=student.id, drive_id=job.id, status=status,
                interview_date=interview_date, feedback=feedback,
                applied_on=datetime.utcnow() - timedelta(days=10)
            )
            db.session.add(application)
            db.session.commit()

            # Placed applications should have a matching Placement row too
            # (normally created inside update_application when status hits
            # "Selected") — doing it manually here since we're skipping that route.
            if status == "Placed":
                existing_placement = Placement.query.filter_by(
                    student_id=student.id, company_id=job.company_id, position=job.title
                ).first()
                if not existing_placement:
                    placement = Placement(
                        student_id=student.id, company_id=job.company_id,
                        position=job.title, salary=job.salary,
                        joining_date=datetime.utcnow() + timedelta(days=30)
                    )
                    db.session.add(placement)
                    db.session.commit()

        print("Demo data seeded successfully.")
        print("\nLogin credentials:")
        print("  Admin    -> use your DEFAULT_ADMIN_EMAIL / DEFAULT_ADMIN_PASSWORD from .env")
        print("  Company  -> hr@techsphere.com / pass123  (approved, has active + closed jobs)")
        print("  Company  -> hiring@brightgrid.com / pass123  (still pending admin approval)")
        print("  Student  -> aarav.sharma@univ.edu / pass123  (already Placed at TechSphere)")
        print("  Student  -> ananya.rao@univ.edu / pass123  (has a Placed application + offer letter)")
        print("  Student  -> diya.patel@univ.edu / pass123  (has an upcoming Interview)")


if __name__ == "__main__":
    seed()
