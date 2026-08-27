from extensions import celery, db, mail
from models.application import Application
from models.placement import Placement
from models.company import Company
from datetime import datetime
import os
from flask_mail import Message
from app import create_app

@celery.task
def generate_monthly_report():
    app = create_app()

    with app.app_context():
        print("Generating monthly placement report...")

        total_applications = Application.query.count()
        total_placements = Placement.query.count()

        placement_percentage = 0
        if total_applications > 0:
            placement_percentage = (total_placements / total_applications) * 100

        companies = Company.query.all()
        company_stats = []

        for company in companies:
            placements = Placement.query.filter_by(company_id=company.id).count()
            company_stats.append({
                "company_name": company.company_name,
                "placements": placements
            })

        os.makedirs("reports", exist_ok=True)

        month_name = datetime.now().strftime("%B_%Y")
        filename = f"reports/monthly_report_{month_name}.html"

        with open(filename, "w") as f:
            f.write(f"""
            <html>
            <body>
                <h1>Placement Report - {month_name}</h1>
                <p>Total Applications: {total_applications}</p>
                <p>Total Placements: {total_placements}</p>
                <p>Placement Percentage: {placement_percentage:.2f}%</p>
                <h2>Company-wise Placement Stats</h2>
                <ul>
            """)
            for stat in company_stats:
                f.write(f"<li>{stat['company_name']} - {stat['placements']} placements</li>")
            f.write("</ul></body></html>")

        # Email part — the report file above is already saved to disk at
        # this point, so a mail-server hiccup (e.g. MailHog not running)
        # shouldn't mark the whole task as failed.
        try:
            msg = Message(
                subject=f"Monthly Placement Report - {month_name}",
                recipients=["admin@ppa.com"]   # change if needed
            )

            with open(filename) as f:
                msg.html = f.read()

            mail.send(msg)
            print("Report emailed to admin")
            return "Monthly Report Generated & Sent"

        except Exception as e:
            print(f"Report generated but email failed: {e}")
            return "Monthly Report Generated (email delivery failed)"