import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Predefined settings (auto-picked by Flask & extensions)
    SECRET_KEY = os.getenv("SECRET_KEY", "trekk-secret-key-mad2-2026-production-ready")
    
    # SQLAlchemy (picked by db.init_app)
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", 
        f"sqlite:///{os.path.join(basedir, 'instance', 'trekking.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT (picked by jwt.init_app)
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "trekk-jwt-super-secret-key-mad2-2026-secure")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)

    # Caching (picked by cache.init_app)
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CACHE_TYPE = os.getenv("CACHE_TYPE", "RedisCache")
    CACHE_REDIS_URL = REDIS_URL
    CACHE_DEFAULT_TIMEOUT = 300

    # Celery (picked by celery worker configuration)
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL

    # Custom application settings (accessed manually via app.config in our code)
    INSTANCE_DIR = os.path.join(basedir, "instance")
    EXPORTS_DIR = os.path.join(INSTANCE_DIR, "exports")
    REPORTS_DIR = os.path.join(INSTANCE_DIR, "reports")
    GOOGLE_CHAT_WEBHOOK_URL = os.getenv("GOOGLE_CHAT_WEBHOOK_URL", "")
