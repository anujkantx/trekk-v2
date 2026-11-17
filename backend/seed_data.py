from datetime import date, timedelta
from backend.app import create_app
from backend.extensions import db, cache
from backend.models import User, Trek, Booking, ExportJob
from backend.tasks.export_tasks import export_user_bookings_csv

def seed_users():
    users_data = [
        {
            "username": "admin",
            "email": "admin@trekking.local",
            "password": "admin@123",
            "role": "admin",
            "status": "active",
            "contact_number": "9999900001"
        },
        {
            "username": "staff1",
            "email": "staff1@trekking.local",
            "password": "staff@123",
            "role": "staff",
            "status": "active",
            "contact_number": "9999900002"
        },
        {
            "username": "staff2",
            "email": "staff2@trekking.local",
            "password": "staff@123",
            "role": "staff",
            "status": "active",
            "contact_number": "9999900003"
        },
        {
            "username": "staff3",
            "email": "staff3@trekking.local",
            "password": "staff@123",
            "role": "staff",
            "status": "active",
            "contact_number": "9999900004"
        },
        {
            "username": "staff4",
            "email": "staff4@trekking.local",
            "password": "staff@123",
            "role": "staff",
            "status": "active",
            "contact_number": "9999900005"
        },
        {
            "username": "staff5",
            "email": "staff5@trekking.local",
            "password": "staff@123",
            "role": "staff",
            "status": "active",
            "contact_number": "9999900006"
        },
        {
            "username": "user1",
            "email": "user1@example.com",
            "password": "user@123",
            "role": "user",
            "status": "active",
            "contact_number": "9999900007"
        },
        {
            "username": "user2",
            "email": "user2@example.com",
            "password": "user@123",
            "role": "user",
            "status": "active",
            "contact_number": "9999900008"
        },
        {
            "username": "user3",
            "email": "user3@example.com",
            "password": "user@123",
            "role": "user",
            "status": "active",
            "contact_number": "9999900009"
        },
        {
            "username": "user4",
            "email": "user4@example.com",
            "password": "user@123",
            "role": "user",
            "status": "active",
            "contact_number": "9999900010"
        },
        {
            "username": "user5",
            "email": "user5@example.com",
            "password": "user@123",
            "role": "user",
            "status": "active",
            "contact_number": "9999900011"
        }
    ]

    created_users = {}
    for data in users_data:
        user = User.query.filter(
            (User.username == data["username"]) | (User.email == data["email"])
        ).first()

        if not user:
            user = User(
                username=data["username"],
                email=data["email"],
                role=data["role"],
                status=data["status"],
                contact_number=data["contact_number"]
            )
            user.set_password(data["password"])
            db.session.add(user)
            db.session.flush()
            print(f"[SEED] Created {data['role'].upper()}: '{data['username']}' (Password: {data['password']})")
        else:
            # Sync password and active status
            user.set_password(data["password"])
            user.status = "active"
            print(f"[SEED] Updated {data['role'].upper()}: '{data['username']}' (Password: {data['password']})")

        created_users[data["username"]] = user

    db.session.commit()
    return created_users

def seed_sample_treks(users):
    s1 = users.get("staff1")
    s2 = users.get("staff2")
    s3 = users.get("staff3")
    s4 = users.get("staff4")
    s5 = users.get("staff5")

    today = date.today()
    treks_data = [
        {
            "name": "Kedarkantha Winter Summit",
            "description": "A magnificent snow trek in Govind Pashu National Park. Perfect for beginners with breathtaking views of the Swargarohini and Black Peak ranges.",
            "location": "Sankri, Uttarakhand",
            "difficulty": "Easy",
            "start_date": today + timedelta(days=14),
            "end_date": today + timedelta(days=19),
            "total_slots": 20,
            "available_slots": 20,
            "price": 8500.0,
            "status": "Open",
            "assigned_staff_id": s1.id if s1 else None
        },
        {
            "name": "Hampta Pass & Chandratal",
            "description": "Dramatic crossover trek from the lush green valleys of Kullu to the stark desert landscapes of Spiti, concluding at the crescent-shaped Chandratal lake.",
            "location": "Manali, Himachal Pradesh",
            "difficulty": "Moderate",
            "start_date": today + timedelta(days=25),
            "end_date": today + timedelta(days=30),
            "total_slots": 15,
            "available_slots": 15,
            "price": 12500.0,
            "status": "Open",
            "assigned_staff_id": s2.id if s2 else None
        },
        {
            "name": "Roopkund Mystery Lake Expedition",
            "description": "A challenging high-altitude expedition traversing alpine meadows of Ali and Bedni Bugyal leading to the mysterious skeletal lake at 15,750 feet.",
            "location": "Chamoli, Uttarakhand",
            "difficulty": "Hard",
            "start_date": today + timedelta(days=45),
            "end_date": today + timedelta(days=53),
            "total_slots": 12,
            "available_slots": 12,
            "price": 16000.0,
            "status": "Pending",
            "assigned_staff_id": s3.id if s3 else None
        },
        {
            "name": "Valley of Flowers Monsoon Trail",
            "description": "UNESCO World Heritage site known for its meadows of endemic alpine flowers and diverse flora, nestled in the western Himalayas.",
            "location": "Joshimath, Uttarakhand",
            "difficulty": "Easy",
            "start_date": today + timedelta(days=60),
            "end_date": today + timedelta(days=65),
            "total_slots": 25,
            "available_slots": 25,
            "price": 9500.0,
            "status": "Approved",
            "assigned_staff_id": s4.id if s4 else None
        },
        {
            "name": "Har Ki Dun Autumn Trail",
            "description": "An ancient cradle-shaped valley steeped in mythological folklore, surrounded by snow-covered peaks and alpine vegetation.",
            "location": "Garhwal, Uttarakhand",
            "difficulty": "Easy",
            "start_date": today - timedelta(days=30),
            "end_date": today - timedelta(days=24),
            "total_slots": 20,
            "available_slots": 17,
            "price": 7800.0,
            "status": "Completed",
            "assigned_staff_id": s1.id if s1 else None
        },
        {
            "name": "Brahmatal Winter Lake Trek",
            "description": "Spectacular frozen lake trek offering front-row panoramic views of Mt. Trishul and Mt. Nanda Ghunti.",
            "location": "Chamoli, Uttarakhand",
            "difficulty": "Moderate",
            "start_date": today + timedelta(days=18),
            "end_date": today + timedelta(days=24),
            "total_slots": 18,
            "available_slots": 18,
            "price": 9200.0,
            "status": "Open",
            "assigned_staff_id": s3.id if s3 else None
        },
        {
            "name": "Kuari Pass Alpine Trail",
            "description": "Lord Curzon trail walking through rhododendron forests with unmatched grand vistas of the Nanda Devi sanctuary.",
            "location": "Joshimath, Uttarakhand",
            "difficulty": "Moderate",
            "start_date": today + timedelta(days=35),
            "end_date": today + timedelta(days=40),
            "total_slots": 16,
            "available_slots": 16,
            "price": 8900.0,
            "status": "Open",
            "assigned_staff_id": s5.id if s5 else None
        },
        {
            "name": "Sandakphu Ridge Expedition",
            "description": "The highest point in West Bengal offering stunning views of four of the world's five highest peaks: Everest, Kanchenjunga, Lhotse, and Makalu.",
            "location": "Darjeeling, West Bengal",
            "difficulty": "Easy",
            "start_date": today + timedelta(days=50),
            "end_date": today + timedelta(days=56),
            "total_slots": 20,
            "available_slots": 20,
            "price": 11500.0,
            "status": "Approved",
            "assigned_staff_id": s4.id if s4 else None
        },
        {
            "name": "Kashmir Great Lakes Trail",
            "description": "High-altitude wilderness trekking along seven pristine alpine lakes surrounded by snowfields and wildflower meadows.",
            "location": "Sonamarg, Jammu & Kashmir",
            "difficulty": "Hard",
            "start_date": today + timedelta(days=70),
            "end_date": today + timedelta(days=78),
            "total_slots": 14,
            "available_slots": 14,
            "price": 17500.0,
            "status": "Pending",
            "assigned_staff_id": s3.id if s3 else None
        },
        {
            "name": "Goechala High Altitude Pass",
            "description": "Intense Himalayan expedition bringing you face-to-face with the gargantuan southeastern face of Mt. Kanchenjunga.",
            "location": "Yuksom, Sikkim",
            "difficulty": "Hard",
            "start_date": today + timedelta(days=40),
            "end_date": today + timedelta(days=50),
            "total_slots": 10,
            "available_slots": 10,
            "price": 19000.0,
            "status": "Open",
            "assigned_staff_id": s5.id if s5 else None
        }
    ]

    created_treks = {}
    for data in treks_data:
        trek = Trek.query.filter_by(name=data["name"]).first()
        if not trek:
            trek = Trek(
                name=data["name"],
                description=data["description"],
                location=data["location"],
                difficulty=data["difficulty"],
                start_date=data["start_date"],
                end_date=data["end_date"],
                total_slots=data["total_slots"],
                available_slots=data["available_slots"],
                price=data["price"],
                status=data["status"],
                assigned_staff_id=data["assigned_staff_id"]
            )
            db.session.add(trek)
            db.session.flush()
            print(f"[SEED] Created Trek: '{data['name']}' ({data['status']})")
        else:
            # Reassign staff if needed
            if data["assigned_staff_id"]:
                trek.assigned_staff_id = data["assigned_staff_id"]
            print(f"[INFO] Trek '{data['name']}' updated.")

        created_treks[data["name"]] = trek

    db.session.commit()
    return created_treks

def seed_sample_bookings(users, treks):
    u1 = users.get("user1")
    u2 = users.get("user2")
    u3 = users.get("user3")
    u4 = users.get("user4")
    u5 = users.get("user5")

    kedarkantha = treks.get("Kedarkantha Winter Summit")
    hampta = treks.get("Hampta Pass & Chandratal")
    harkidun = treks.get("Har Ki Dun Autumn Trail")
    vof = treks.get("Valley of Flowers Monsoon Trail")
    brahmatal = treks.get("Brahmatal Winter Lake Trek")
    kuari = treks.get("Kuari Pass Alpine Trail")
    goechala = treks.get("Goechala High Altitude Pass")

    if not u1 or not u2:
        return

    bookings_data = [
        # user1 bookings
        {
            "user": u1,
            "trek": kedarkantha,
            "num_slots": 2,
            "status": "Booked"
        },
        {
            "user": u1,
            "trek": harkidun,
            "num_slots": 1,
            "status": "Completed"
        },
        {
            "user": u1,
            "trek": vof,
            "num_slots": 1,
            "status": "Cancelled"
        },
        # user2 bookings
        {
            "user": u2,
            "trek": kedarkantha,
            "num_slots": 1,
            "status": "Booked"
        },
        {
            "user": u2,
            "trek": hampta,
            "num_slots": 2,
            "status": "Booked"
        },
        {
            "user": u2,
            "trek": harkidun,
            "num_slots": 2,
            "status": "Completed"
        },
        # user3 bookings
        {
            "user": u3,
            "trek": brahmatal,
            "num_slots": 2,
            "status": "Booked"
        },
        {
            "user": u3,
            "trek": kedarkantha,
            "num_slots": 1,
            "status": "Completed"
        },
        # user4 bookings
        {
            "user": u4,
            "trek": kuari,
            "num_slots": 2,
            "status": "Booked"
        },
        {
            "user": u4,
            "trek": hampta,
            "num_slots": 1,
            "status": "Booked"
        },
        {
            "user": u4,
            "trek": vof,
            "num_slots": 1,
            "status": "Cancelled"
        },
        # user5 bookings
        {
            "user": u5,
            "trek": goechala,
            "num_slots": 1,
            "status": "Booked"
        },
        {
            "user": u5,
            "trek": brahmatal,
            "num_slots": 1,
            "status": "Booked"
        },
        {
            "user": u5,
            "trek": harkidun,
            "num_slots": 1,
            "status": "Completed"
        }
    ]

    for item in bookings_data:
        u = item["user"]
        t = item["trek"]
        if not u or not t:
            continue

        existing = Booking.query.filter_by(
            user_id=u.id, trek_id=t.id, status=item["status"]
        ).first()

        if not existing:
            booking = Booking(
                user_id=u.id,
                trek_id=t.id,
                num_slots=item["num_slots"],
                status=item["status"]
            )
            if item["status"] == "Booked" and t.available_slots >= item["num_slots"]:
                t.available_slots -= item["num_slots"]

            db.session.add(booking)
            print(f"[SEED] Created Booking: {u.username} -> '{t.name}' ({item['num_slots']} slots, {item['status']})")
        else:
            print(f"[INFO] Booking for {u.username} on '{t.name}' already exists.")

    db.session.commit()

    # Pre-generate an export job for user1 & user2 so CSV download is ready
    for target_user in [u1, u2]:
        existing_job = ExportJob.query.filter_by(user_id=target_user.id, status="COMPLETED").first()
        if not existing_job:
            job = ExportJob(user_id=target_user.id, status="PENDING")
            db.session.add(job)
            db.session.commit()
            try:
                export_user_bookings_csv(job.id)
                print(f"[SEED] Pre-generated CSV Export for {target_user.username} (Job #{job.id})")
            except Exception:
                pass

def run_seed():
    app = create_app()
    with app.app_context():
        db.create_all()
        print("Database structure verified.")
        users = seed_users()
        treks = seed_sample_treks(users)
        seed_sample_bookings(users, treks)

        try:
            cache.clear()
            print("Redis cache refreshed with seeded data.")
        except Exception:
            pass

        print("\nAll seed data (admin, staff1-5, user1-5, Treks, Bookings) inserted successfully!")

if __name__ == "__main__":
    run_seed()
