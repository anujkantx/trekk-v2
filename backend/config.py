import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "trekk-secret-key-mad2-2026")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "trekk-jwt-secret-key-2026")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)
    
    # Programmatic SQLite database path
    INSTANCE_DIR = os.path.join(basedir, "instance")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", 
        f"sqlite:///{os.path.join(INSTANCE_DIR, 'trekking.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Redis configuration
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CACHE_TYPE = os.getenv("CACHE_TYPE", "RedisCache")
    CACHE_REDIS_URL = REDIS_URL
    CACHE_DEFAULT_TIMEOUT = 300

    # Celery configuration
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL
    
    # Export and Report directories (inside instance for clean structure & gitignore)
    EXPORTS_DIR = os.path.join(INSTANCE_DIR, "exports")
    REPORTS_DIR = os.path.join(INSTANCE_DIR, "reports")
    
    # Webhook / Email simulation
    GOOGLE_CHAT_WEBHOOK_URL = os.getenv("GOOGLE_CHAT_WEBHOOK_URL", "")
