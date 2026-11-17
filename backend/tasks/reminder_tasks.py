from datetime import date, timedelta
from celery import shared_task
from backend.extensions import db
from backend.models.booking import Booking
from backend.models.trek import Trek

@shared_task(name="tasks.send_daily_trek_reminders")
def send_daily_trek_reminders():
    # Scan for bookings of treks starting tomorrow
    tomorrow = date.today() + timedelta(days=1)
    upcoming_bookings = (
        Booking.query.join(Trek)
        .filter(Trek.start_date == tomorrow, Booking.status == "Booked")
        .all()
    )

    reminders_sent = 0
    for booking in upcoming_bookings:
        user = booking.user
        trek = booking.trek
        # Log notification / send simulated reminder
        print(f"[REMINDER] Dear {user.username}, your trek '{trek.name}' starts tomorrow ({tomorrow})!")
        reminders_sent += 1

    return {"status": "success", "reminders_sent": reminders_sent}
