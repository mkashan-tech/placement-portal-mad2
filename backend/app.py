from flask import Flask
from extensions import db, celery, cache, mail
from models.user import User
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.company import company_bp
from routes.student import student_bp
# ===================================
#                    WSL
#  cd "/mnt/c/Users/Mohammad Kashan/Projects/placement_portal_v2_23F2003821/backend"
#  source venv/bin/activate
#  celery -A celery_worker.celery worker --loglevel=info
#  celery -A celery_worker.celery beat --loglevel=info
#  ./MailHog_linux_amd64
# =====================================
def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///placement.db"
    app.secret_key = "secret"

    # MailHog config
    app.config["MAIL_SERVER"] = "127.0.0.1"
    app.config["MAIL_PORT"]  = 1025
    app.config["MAIL_USE_TLS"] = False
    app.config["MAIL_USE_SSL"] = False
    app.config["MAIL_USERNAME"] = None
    app.config["MAIL_PASSWORD"] = None
    app.config["MAIL_DEFAULT_SENDER"] = ("Placement Portal", "placement@portal.com")


    db.init_app(app)
    cache.init_app(app)
    mail.init_app(app)

# registering blueprint
    app.register_blueprint(auth_bp, url_prefix="/api")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(company_bp, url_prefix="/api/company")
    app.register_blueprint(student_bp, url_prefix="/api/student")

    with app.app_context():
        db.create_all()

# ======================        
# Creating default admin
# ======================
        admin = User.query.filter_by(role="admin").first()
        if not admin:
            admin = User(
                email="admin@ppa.com",
                password="admin",
                role="admin",
                is_active=True
            )
            db.session.add(admin)
            db.session.commit()
            print("Admin Created!")

    @app.route("/")
    def home():
        return "Placement Portal API running."

    return app


app = create_app()


# Bind Flask context to Celery
class ContextTask(celery.Task):
    def __call__(self, *args, **kwargs):
        with app.app_context():
            return self.run(*args, **kwargs)

celery.Task = ContextTask

# This must be in last

if __name__ == "__main__":
    app.run(debug=True)