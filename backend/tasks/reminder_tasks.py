from extensions import celery, mail
from flask_mail import Message
from models.application import Application
from models.student import Student
from models.user import User
from datetime import datetime, timedelta

@celery.task
def send_interview_reminders():
    print("Running interview reminder task...")

    tomorrow_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    tomorrow_end = tomorrow_start + timedelta(days=1)

    applications = Application.query.filter(
        Application.status == "Interview",
        Application.interview_date >= tomorrow_start,
        Application.interview_date <= tomorrow_end
    ).all()


    for app in applications:

        student = Student.query.get(app.student_id)
        user = User.query.get(student.user_id)

        msg = Message(
            subject = "Interview Reminder",
            recipients = [user.email],
            body = f"Dear {student.name},\n\nYour interview is scheduled on {app.interview_date}.\n\nBest of luck!"
        )

        mail.send(msg)


        #sending remidner
        print(f"Reminder sent to {user.email} for interview on {app.interview_date}")

    return f"Sent{len(applications)} reminders"