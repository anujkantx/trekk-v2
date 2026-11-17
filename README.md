# Trekking Management Application (TMA)

Developer quickstart guide to set up and run the application locally on Windows.

---

## 📦 Prerequisites

- **Python**: 3.11+
- **Node.js**: v18+ & npm
- **Redis**: Docker Desktop (or local Redis on port 6379)

---

## ⚙️ 1. Setup (One-Time)

Run the automated setup script in the project root:
```cmd
setup.bat
```

*Or run manually via terminal:*
```powershell
# Backend virtual environment & dependencies
python -m venv backend\.venv
.\backend\.venv\Scripts\activate.bat
pip install -r backend\requirements.txt

# Initialize SQLite database & seed demo accounts
python -m backend.init_db

# Frontend dependencies
cd frontend
npm install
cd ..
```

---

## 🚀 2. Run the Application (4 Terminals)

Open 4 separate terminal windows in the project root directory:

### Terminal 0: Start Redis (Docker)
```powershell
docker compose up -d
```
*(Ensures Redis is listening on `localhost:6379`)*

### Terminal 1: Flask Backend API (Port 5001)
```cmd
backend.bat
```
*Or manual:* `.\backend\.venv\Scripts\python.exe -m backend.app`

### Terminal 2: Celery Worker (Pool: solo)
```cmd
celery_worker.bat
```
*Or manual:* `.\backend\.venv\Scripts\python.exe -m celery -A backend.celery_app.celery_app worker --loglevel=info --pool=solo`

### Terminal 3: Celery Beat Scheduler
```cmd
celery_beat.bat
```
*Or manual:* `.\backend\.venv\Scripts\python.exe -m celery -A backend.celery_app.celery_app beat --loglevel=info`

### Terminal 4: Vue 3 Frontend (Port 5173)
```cmd
frontend.bat
```
*Or manual:* `cd frontend && npm run dev`

---

## 🌐 Endpoints & URLs

| Service | URL | Description |
| :--- | :--- | :--- |
| **Frontend App** | http://localhost:5173 | Vue 3 + Bootstrap 5 UI |
| **Backend REST API** | http://localhost:5001/api | Flask REST endpoints |
| **Redis Broker** | `localhost:6379` | Cache & task message broker |

---

## 🔑 Demo Credentials

| Role | Email | Password |
| :--- | :--- | :--- |
| **Admin** | `admin@trekking.local` | `admin@123` |
| **Staff** | `staff1@trekking.local` *(staff1 to staff5)* | `staff@123` |
| **Trekker** | `user1@example.com` *(user1 to user5)* | `user@123` |
