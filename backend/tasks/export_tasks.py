# tasks/export_tasks.py - Updated

from extensions import celery
import csv
import os
from datetime import datetime

@celery.task
def export_csv(data, filename):
    """Export data to CSV"""
    # Create exports directory
    os.makedirs("exports", exist_ok=True)
    
    filepath = os.path.join("exports", filename)
    
    with open(filepath, mode="w", newline="") as file:
        if data and isinstance(data[0], dict):
            # Dict data
            writer = csv.DictWriter(file, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        else:
            # List data
            writer = csv.writer(file)
            writer.writerow([
                "Student ID", "Company", "Job Title",
                "Status", "Applied On", "Interview Date"
            ])
            for row in data:
                writer.writerow(row)
    
    print(f"CSV Export completed: {filename}")
    return {"status": "completed", "filename": filename}


@celery.task
def export_applications_csv(data, filename):
    """Export applications data to CSV"""
    os.makedirs("exports", exist_ok=True)
    
    filepath = os.path.join("exports", filename)
    
    with open(filepath, mode="w", newline="") as file:
        if data and isinstance(data[0], dict):
            writer = csv.DictWriter(file, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
    
    print(f"Applications export completed: {filename}")
    return {"status": "completed", "filename": filename}