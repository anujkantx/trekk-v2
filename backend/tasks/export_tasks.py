import csv
import os
from datetime import datetime
from celery import shared_task
from flask import current_app
from backend.extensions import db
from backend.models.export_job import ExportJob
from backend.models.booking import Booking

@shared_task(name="tasks.export_user_bookings_csv")
def export_user_bookings_csv(job_id):
    job = db.session.get(ExportJob, job_id)
    if not job:
        return {"status": "error", "message": f"ExportJob {job_id} not found"}

    try:
        job.status = "PROCESSING"
        db.session.commit()

        bookings = (
            Booking.query.filter_by(user_id=job.user_id)
            .order_by(Booking.booking_date.desc())
            .all()
        )

        exports_dir = current_app.config.get("EXPORTS_DIR")
        os.makedirs(exports_dir, exist_ok=True)

        filename = f"booking_history_user_{job.user_id}_job_{job.id}.csv"
        file_path = os.path.join(exports_dir, filename)

        with open(file_path, mode="w", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow([
                "Booking ID",
                "Trek Name",
                "Location",
                "Difficulty",
                "Start Date",
                "End Date",
                "Slots Booked",
                "Price Per Slot (INR)",
                "Total Amount (INR)",
                "Booking Status",
                "Booked At"
            ])

            for b in bookings:
                trek = b.trek
                total_amount = (trek.price * b.num_slots) if trek else 0.0
                writer.writerow([
                    b.id,
                    trek.name if trek else "N/A",
                    trek.location if trek else "N/A",
                    trek.difficulty if trek else "N/A",
                    trek.start_date.isoformat() if trek and trek.start_date else "N/A",
                    trek.end_date.isoformat() if trek and trek.end_date else "N/A",
                    b.num_slots,
                    f"{trek.price:.2f}" if trek else "0.00",
                    f"{total_amount:.2f}",
                    b.status,
                    b.booking_date.strftime("%Y-%m-%d %H:%M:%S") if b.booking_date else "N/A"
                ])

        job.status = "COMPLETED"
        job.file_path = file_path
        job.completed_at = datetime.utcnow()
        db.session.commit()

        return {
            "status": "success",
            "job_id": job.id,
            "file_path": file_path,
            "total_records": len(bookings)
        }

    except Exception as e:
        job.status = "FAILED"
        db.session.commit()
        raise e
