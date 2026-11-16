from backend.app import create_app
from backend.extensions import db
from backend.models import User, Trek, Booking, ExportJob

def init_database():
    app = create_app()
    with app.app_context():
        # Create all tables programmatically
        db.create_all()
        print("Database tables created successfully.")

        admin = User.query.filter_by(role="admin").first()

        if not admin:
            admin = User(
                username="admin",
                email="admin@trekking.local",
                role="admin",
                status="active",
                contact_number="9999999999"
            )
            admin.set_password("Admin@123")
            db.session.add(admin)
            db.session.commit()

            print("Default Admin user created successfully (username: 'admin', password: 'Admin@123').")
        else:
            print("Admin user already exists.")

if __name__ == "__main__":
    init_database()
