import os
from datetime import datetime
from celery import shared_task
from flask import current_app
from backend.extensions import db
from backend.models.user import User
from backend.models.trek import Trek
from backend.models.booking import Booking

@shared_task(name="tasks.generate_monthly_activity_report")
def generate_monthly_activity_report():
    reports_dir = current_app.config.get("REPORTS_DIR")
    os.makedirs(reports_dir, exist_ok=True)

    now = datetime.utcnow()
    filename = f"monthly_report_{now.year}_{now.month:02d}.pdf"
    file_path = os.path.join(reports_dir, filename)

    # Basic report metadata
    total_users = User.query.filter_by(role="user").count()
    total_treks = Trek.query.count()
    total_bookings = Booking.query.count()

    # Generate PDF using ReportLab
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas

        c = canvas.Canvas(file_path, pagesize=letter)
        c.drawString(100, 750, f"Monthly Platform Activity Report - {now.strftime('%B %Y')}")
        c.drawString(100, 720, f"Generated On: {now.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        c.drawString(100, 680, f"Total Registered Trekkers: {total_users}")
        c.drawString(100, 660, f"Total Treks Hosted: {total_treks}")
        c.drawString(100, 640, f"Total Bookings Processed: {total_bookings}")
        c.save()

        return {
            "status": "success",
            "file_path": file_path,
            "generated_at": now.isoformat()
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
