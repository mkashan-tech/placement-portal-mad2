from app import app   # ensures Flask app is created
from extensions import celery
from celery.schedules import crontab

celery.conf.timezone = "Asia/Kolkata"

celery.conf.beat_schedule = {
    "daily-interview-reminder": {
        "task": "tasks.reminder_tasks.send_interview_reminders",
        "schedule": crontab(hour=9, minute=0),
        #"schedule": crontab(minute="*/1"),
    },
    "monthly-report": {
        "task": "tasks.report_tasks.generate_monthly_report",
        #"schedule": crontab(minute="*/1"),
        "schedule": crontab(day_of_month=1, hour=8, minute=0),
    }
}

import tasks.reminder_tasks
import tasks.export_tasks
import tasks.report_tasks