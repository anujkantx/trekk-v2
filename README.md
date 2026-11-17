# Trekking Management Application (TMA) - V2
### IIT Madras BS Degree — Modern Application Development 2 (MAD-2)

A production-ready full-stack trekking management web application built using **Flask REST APIs**, **SQLite (SQLAlchemy ORM)**, **Redis Caching**, **Celery Asynchronous Batch Jobs**, and a **Vue.js 3 Single Page Application (SPA)** styled strictly with **Bootstrap 5**.

---

## 🛠️ Architecture & Tech Stack

```
                                +---------------------------+
                                |      Vue.js Frontend      |
                                |   (Bootstrap 5 Styling)   |
                                +-------------+-------------+
                                              |
                                              | HTTP / JSON Requests
                                              | (JWT in Bearer Header)
                                              v
                                +---------------------------+
                                |      Flask REST APIs      |
                                +-------+-----------+-------+
                                        |           |
                      +-----------------+           +-----------------+
                      |                                               |
                      v                                               v
          +-----------------------+                       +-----------------------+
          |     SQLite Database   |                       |      Redis Cache      |
          |   (via SQLAlchemy)    |                       | (Frequent Read Data)  |
          +-----------------------+                       +-----------+-----------+
                                                                      |
                                                                      | Message Broker
                                                                      v
                                                          +-----------------------+
                                                          |    Celery Workers     |
                                                          | (Reminders, Reports,  |
                                                          |      CSV Export)      |
                                                          +-----------------------+
```

| Layer | Technology | Details |
| :--- | :--- | :--- |
| **Backend** | Python 3.13 / Flask | RESTful architecture, application factory pattern, Blueprint modularity |
| **Auth & RBAC** | Flask-JWT-Extended | Stateless JWT authentication, role decorators (`Admin`, `Staff`, `User`) |
| **Database** | SQLite via SQLAlchemy | Programmatic creation (`db.create_all()`), cascading relationships, locking |
| **Caching** | Redis (Docker) / Flask-Caching | In-memory key-value cache with automated cache invalidation on mutations |
| **Async Tasks** | Celery + Redis Broker | Background CSV exports, daily trek reminders, monthly PDF activity reports |
| **Frontend** | Vue 3 + Vite | Single Page Application (SPA), Vue Router navigation guards, Pinia/localStorage |
| **UI Framework** | Bootstrap 5 + Bootstrap Icons | Clean, responsive UI with zero external CSS frameworks (No Tailwind/Bulma) |

---

## 🔑 Demo Seed Accounts

The database comes pre-seeded with 11 standardized accounts and realistic Himalayan treks & bookings:

| Role | Username | Email | Password | Access / Assigned Treks |
| :--- | :--- | :--- | :--- | :--- |
| **Admin** | `admin` | `admin@trekking.local` | `admin@123` | Full control, revenue analytics charts, user moderation, staff onboarding |
| **Staff 1** | `staff1` | `staff1@trekking.local` | `staff@123` | Assigned to Kedarkantha, Har Ki Dun |
| **Staff 2** | `staff2` | `staff2@trekking.local` | `staff@123` | Assigned to Hampta Pass |
| **Staff 3** | `staff3` | `staff3@trekking.local` | `staff@123` | Assigned to Roopkund, Brahmatal, Kashmir Great Lakes |
| **Staff 4** | `staff4` | `staff4@trekking.local` | `staff@123` | Assigned to Valley of Flowers, Sandakphu |
| **Staff 5** | `staff5` | `staff5@trekking.local` | `staff@123` | Assigned to Kuari Pass, Goechala |
| **Trekker 1** | `user1` | `user1@example.com` | `user@123` | Bookings on Kedarkantha, Har Ki Dun; Pre-generated CSV ready |
| **Trekker 2** | `user2` | `user2@example.com` | `user@123` | Bookings on Kedarkantha, Hampta Pass; Pre-generated CSV ready |
| **Trekker 3** | `user3` | `user3@example.com` | `user@123` | Bookings on Brahmatal, Kedarkantha |
| **Trekker 4** | `user4` | `user4@example.com` | `user@123` | Bookings on Kuari Pass, Hampta Pass, Valley of Flowers |
| **Trekker 5** | `user5` | `user5@example.com` | `user@123` | Bookings on Goechala, Brahmatal, Har Ki Dun |

---

## 🚀 10-Minute Local Boot Instructions (Windows)

### Prerequisites
- Python 3.11+
- Node.js 18+ & npm
- Docker Desktop (for Redis container)

### Step 1: Start Redis
Start the Redis container using Docker Compose:
```powershell
docker compose up -d
```
*(Runs Redis on `localhost:6379`).*

### Step 2: Initialize & Seed Database (Optional)
Database initializes automatically on first boot, or run manually:
```powershell
backend\.venv\Scripts\python.exe -m backend.seed_data
```

### Step 3: Run the Application
Open 3 terminal windows and run the one-click launcher scripts:

* **Terminal 1: Flask Backend Server**
  ```powershell
  .\backend.bat
  ```
  *Server starts on `http://localhost:5001`*

* **Terminal 2: Vue 3 Frontend Client**
  ```powershell
  .\frontend.bat
  ```
  *Vite dev server starts on `http://localhost:5173`*

* **Terminal 3: Celery Background Worker**
  ```powershell
  .\celery_worker.bat
  ```
  *Celery worker starts using `--pool=solo` (Windows compatible)*

*(Optional)* **Terminal 4: Celery Beat Scheduler**
```powershell
.\celery_beat.bat
```
*Schedules daily reminders (8:00 AM) and monthly PDF reports (1st of month).*

---

## 📁 Project Directory Structure

```
trekk-v2/
├── backend/
│   ├── instance/              # SQLite DB, CSV exports, PDF reports
│   ├── models/                # User, Trek, Booking, ExportJob
│   ├── routes/                # auth, treks, bookings, admin REST endpoints
│   ├── tasks/                 # Celery async tasks (export, reminder, report)
│   ├── utils/                 # RBAC decorators (@admin_required, etc.)
│   ├── app.py                 # Application factory
│   ├── celery_app.py          # Celery configuration & Beat schedule
│   ├── config.py              # Centralized environment settings
│   ├── extensions.py          # db, jwt, cache, cors instances
│   ├── init_db.py             # Programmatic database setup
│   └── seed_data.py           # Standardized demo data seeder
├── frontend/
│   ├── src/
│   │   ├── components/        # Navbar.vue
│   │   ├── router/            # Navigation guards & RBAC routing
│   │   ├── views/             # Home, TrekDetail, Login, Register, Dashboards
│   │   ├── api.js             # Central Axios client with JWT interceptor
│   │   └── App.vue            # Root component
│   └── index.html             # Entry HTML
├── notes/                     # In-depth architectural & conceptual guides
├── docs/                      # Course requirement documents & plan
├── backend.bat                # 1-click backend runner
├── frontend.bat               # 1-click frontend runner
├── celery_worker.bat          # 1-click Celery worker runner
├── celery_beat.bat            # 1-click Celery beat scheduler
└── docker-compose.yml         # Redis container service
```
