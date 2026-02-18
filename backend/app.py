from flask import Flask
from models.db import db
from models import user, company, student, drive, application
from models.user import User

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///placement.db"
db.init_app(app)

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

if __name__ == "__main__":
    app.run(debug=True)


