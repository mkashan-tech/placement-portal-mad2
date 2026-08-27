import os
from dotenv import load_dotenv
from flask import Flask, render_template
from extensions import db, celery, cache, mail
from models.user import User
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.company import company_bp
from routes.student import student_bp
from extensions import db

load_dotenv()


# ===================================
# Local dev quick-reference (run from backend/):
#  source venv/bin/activate
#  celery -A celery_worker.celery worker --loglevel=info
#  celery -A celery_worker.celery beat --loglevel=info
#  ./MailHog_linux_amd64
#  http://localhost:8025
# =====================================
def create_app():
    app = Flask(
        __name__,
        template_folder="../frontend/templates",
        static_folder="../frontend/static"
    )
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///placement.db")
    app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-key-change-in-production")
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["SESSION_COOKIE_SECURE"] = False

    # MailHog config (local dev email testing)
    app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER", "127.0.0.1")
    app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT", 1025))
    app.config["MAIL_USE_TLS"] = os.getenv("MAIL_USE_TLS", "False") == "True"
    app.config["MAIL_USE_SSL"] = False
    app.config["MAIL_USERNAME"] = None
    app.config["MAIL_PASSWORD"] = None
    app.config["MAIL_DEFAULT_SENDER"] = ("Placement Portal", os.getenv("MAIL_DEFAULT_SENDER", "placement@portal.com"))

# work
    db.init_app(app)
    cache.init_app(app)
    mail.init_app(app)


# registering blueprint
    app.register_blueprint(auth_bp, url_prefix="/api")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(company_bp, url_prefix="/api/company")
    app.register_blueprint(student_bp, url_prefix="/api/student")
    from routes.tasks import tasks_bp
    app.register_blueprint(tasks_bp, url_prefix="/api/tasks")

    with app.app_context():
        db.create_all()

# ======================        
# Creating default admin
# ======================
        admin = User.query.filter_by(role="admin").first()
        if not admin:
            admin = User(
                email=os.getenv("DEFAULT_ADMIN_EMAIL", "admin@ppa.com"),
                role="admin",
                is_active=True
            )
            admin.set_password(os.getenv("DEFAULT_ADMIN_PASSWORD", "admin123"))
            db.session.add(admin)
            db.session.commit()
            print("Default admin created (see .env.example for credential config).")

    @app.route("/")
    def home():
        return render_template("index.html")

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