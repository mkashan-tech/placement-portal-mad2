from extensions import celery
import csv

@celery.task
def export_csv(data, filename):
    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Job", "Status", "Date"])

        for row in data:
            writer.writerow(row)

    print("CSV Export completed.")
    return "Done"