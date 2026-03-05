from extensions import celery, db
from models.application import Application
from models.placement import Placement
from models.company import Company
from datetime import datetime
import os

@celery.task
def generate_monthly_report():
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
        <head>
            <title>Monthly Placement Report</title>
        </head>
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

        f.write("""
            </ul>
        </body>
        </html>
        """)

    print(f"Report saved as {filename}")
    return "Monthly Report Generated"