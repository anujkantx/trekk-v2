from backend.app import create_app
from backend.extensions import db
from backend.seed_data import seed_users, seed_sample_treks, seed_sample_bookings

def init_database():
    app = create_app()
    with app.app_context():
        # Create all tables programmatically
        db.create_all()
        print("Database tables created successfully.")
        users = seed_users()
        treks = seed_sample_treks(users)
        seed_sample_bookings(users, treks)

if __name__ == "__main__":
    init_database()
