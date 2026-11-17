from celery import Celery
from celery.schedules import crontab
from backend.app import create_app

def make_celery(app):
    celery = Celery(
        app.import_name,
        broker=app.config.get("CELERY_BROKER_URL", "redis://localhost:6379/0"),
        backend=app.config.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/0"),
        include=[
            "backend.tasks.export_tasks",
            "backend.tasks.reminder_tasks",
            "backend.tasks.report_tasks"
        ]
    )

    celery.conf.update(
        timezone="Asia/Kolkata",
        enable_utc=False,
        task_track_started=True,
        result_extended=True,
        broker_connection_retry_on_startup=True
    )

    celery.conf.beat_schedule = {
        "daily-trek-reminders-at-8am": {
            "task": "tasks.send_daily_trek_reminders",
            "schedule": crontab(hour=8, minute=0),
        },
        "monthly-activity-report-on-1st": {
            "task": "tasks.generate_monthly_activity_report",
            "schedule": crontab(day_of_month="1", hour=0, minute=0),
        },
    }

    class FlaskTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = FlaskTask
    return celery

flask_app = create_app()
celery_app = make_celery(flask_app)

import backend.tasks.export_tasks
import backend.tasks.reminder_tasks
import backend.tasks.report_tasks
