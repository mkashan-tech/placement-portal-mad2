from flask import Flask
from models.db import db
from models import user, company, student, drive, application, placement
from models.user import User
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.company import company_bp
from routes.student import student_bp

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///placement.db"
app.secret_key = "secret"

db.init_app(app)

# Register Blueprint
app.register_blueprint(auth_bp, url_prefix="/api")
app.register_blueprint(admin_bp, url_prefix="/api/admin")
app.register_blueprint(company_bp, url_prefix="/api/company")
app.register_blueprint(student_bp, url_prefix="/api/student")

with app.app_context():
    db.create_all()

    # Creating default admin
    admin = User.query.filter_by(role="admin").first()
    if not admin:
        admin = User(
            email="admin.placement@gmail.com",
            password="admin123",
            role="admin",
            is_active=True
        )
        db.session.add(admin)
        db.session.commit()
        print("Admin Created!")

@app.route('/')
def home():
    return "Placement Portal API running."


# This part must be in end.
if __name__ == "__main__":
    app.run(debug=True)
