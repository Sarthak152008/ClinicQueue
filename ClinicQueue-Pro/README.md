# ClinicQueue Healthcare Platform

ClinicQueue is a FastAPI + SQLAlchemy + SQLite diagnostic booking platform with a responsive React/Vite frontend.

## Run locally

```bash
cd ClinicQueue-Pro
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # set a real CLINICQUEUE_SECRET_KEY
cd backend
PYTHONPATH=. python init_db.py
PYTHONPATH=. uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

In a second terminal:

```bash
cd ClinicQueue-Pro/frontend
npm install
npm run dev
```

The frontend runs at `http://localhost:5173` and the API/docs at `http://127.0.0.1:8000/docs`.

## Demo credentials

- Patient: `demo@clinicqueue.com` / `demo123456`
- Admin: `admin@clinicqueue.com` / `admin123456`
- Doctor: `doctor@clinicqueue.com` / `doctor123456`

## Included workflows

- Patient registration, JWT login/logout, profile, package browsing, live slot selection, booking history and dashboard.
- Package details including price, category, included tests, preparation and report time.
- Online payment adapter flow with transaction/reference recording and cash-at-hospital payments kept as `pending`.
- Admin/staff package and slot management, booking monitoring and statistics.
- Doctor/staff appointment monitoring with patient, package, token and status details.
- Booking cancellation for patients, doctors/staff and admins with confirmation in the UI, slot release, `cancelled` booking/payment states, and a persistent cancellation audit history.
- SQLAlchemy relationships for users, doctors, packages, slots, bookings, payments and appointments.

For a separately hosted API, set `VITE_API_URL` in the frontend environment. Never commit `.env` or production secrets.

## Cancellation API

Authenticated users can cancel through:

```text
POST /api/bookings/{booking_id}/cancel
Body: { "reason": "Optional reason" }
```

Patients may cancel their own pending/confirmed bookings. Doctors, staff and admins may cancel any pending/confirmed booking. The endpoint marks the booking and related payment as `cancelled`, releases one capacity unit on the time slot, and writes an immutable record to `booking_cancellations`. Cancellation history is available at `GET /api/bookings/{booking_id}/cancellations`.
