from datetime import datetime
from backend.extensions import db

class ExportJob(db.Model):
    __tablename__ = "export_jobs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="PENDING") # 'PENDING', 'COMPLETED', 'FAILED'
    file_path = db.Column(db.String(256), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)

    # Relationship to requesting user
    user = db.relationship("User", backref=db.backref("export_jobs", cascade="all, delete-orphan"))

    def __init__(self, user_id, status="PENDING", file_path=None):
        self.user_id = user_id
        self.status = status
        self.file_path = file_path

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "status": self.status,
            "file_path": self.file_path,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }
