import os
import secrets
from datetime import date, datetime, timedelta
from typing import List

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session, joinedload

from auth import create_access_token, hash_password, verify_password, verify_token
from database import get_db, init_db
from models import Booking, BookingCancellation, Doctor, Package, Payment, TimeSlot, User
from schemas import (
    BookingCreate, BookingDetailResponse, BookingResponse, BookingUpdate, CancellationRequest,
    CancellationResponse, DashboardStats,
    PackageCreate, PackageResponse, PackageUpdate, PatientStats, PaymentCreate, PaymentResponse,
    TimeSlotCreate, TimeSlotResponse, TokenResponse, UserLogin, UserProfileUpdate,
    UserRegister, UserResponse,
)

app = FastAPI(title="ClinicQueue Healthcare Platform", version="4.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    init_db()

@app.get("/")
def home():
    return {"name": "ClinicQueue", "message": "Healthcare diagnostic booking platform", "version": app.version}

@app.get("/api/health")
def health():
    return {"status": "ok", "database": "connected"}

def current_user(email: str, db: Session) -> User:
    user = db.query(User).filter(User.email == email).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User account is unavailable")
    return user

def require_roles(user: User, *roles: str):
    if user.role not in roles:
        raise HTTPException(status_code=403, detail="You do not have permission for this action")

def booking_detail(booking: Booking) -> dict:
    return {
        **BookingResponse.model_validate(booking).model_dump(),
        "patient": UserResponse.model_validate(booking.patient),
        "package": PackageResponse.model_validate(booking.package),
        "cancellations": [CancellationResponse.model_validate(item) for item in booking.cancellations],
        "payment_status": booking.payment.payment_status if booking.payment else None,
    }

@app.post("/api/auth/register", response_model=TokenResponse, status_code=201)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=409, detail="Email already registered")
    user = User(**user_data.model_dump(exclude={"password"}), password_hash=hash_password(user_data.password), role="patient")
    db.add(user); db.commit(); db.refresh(user)
    return {"access_token": create_access_token({"sub": user.email}), "token_type": "bearer", "user": user, "role": user.role}

@app.post("/api/auth/login", response_model=TokenResponse)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="User account is inactive")
    return {"access_token": create_access_token({"sub": user.email}), "token_type": "bearer", "user": user, "role": user.role}

@app.get("/api/auth/me", response_model=UserResponse)
def get_me(email: str = Depends(verify_token), db: Session = Depends(get_db)):
    return current_user(email, db)

@app.put("/api/users/profile", response_model=UserResponse)
def update_profile(data: UserProfileUpdate, email: str = Depends(verify_token), db: Session = Depends(get_db)):
    user = current_user(email, db)
    for key, value in data.model_dump(exclude_unset=True).items(): setattr(user, key, value)
    db.commit(); db.refresh(user)
    return user

@app.get("/api/packages", response_model=List[PackageResponse])
def list_packages(db: Session = Depends(get_db)):
    return db.query(Package).filter(Package.is_active.is_(True)).order_by(Package.category, Package.price).all()

@app.get("/api/packages/{package_id}", response_model=PackageResponse)
def get_package(package_id: int, db: Session = Depends(get_db)):
    package = db.query(Package).filter(Package.id == package_id, Package.is_active.is_(True)).first()
    if not package: raise HTTPException(status_code=404, detail="Package not found")
    return package

@app.post("/api/admin/packages", response_model=PackageResponse, status_code=201)
def create_package(data: PackageCreate, email: str = Depends(verify_token), db: Session = Depends(get_db)):
    require_roles(current_user(email, db), "admin", "staff")
    package = Package(**data.model_dump()); db.add(package); db.commit(); db.refresh(package)
    return package

@app.put("/api/admin/packages/{package_id}", response_model=PackageResponse)
def update_package(package_id: int, data: PackageUpdate, email: str = Depends(verify_token), db: Session = Depends(get_db)):
    require_roles(current_user(email, db), "admin", "staff")
    package = db.query(Package).filter(Package.id == package_id).first()
    if not package: raise HTTPException(status_code=404, detail="Package not found")
    for key, value in data.model_dump(exclude_unset=True).items(): setattr(package, key, value)
    db.commit(); db.refresh(package); return package

@app.post("/api/admin/time-slots", response_model=TimeSlotResponse, status_code=201)
def create_slot(data: TimeSlotCreate, email: str = Depends(verify_token), db: Session = Depends(get_db)):
    require_roles(current_user(email, db), "admin", "staff")
    if not db.query(Package).filter(Package.id == data.package_id, Package.is_active.is_(True)).first():
        raise HTTPException(status_code=404, detail="Package not found")
    if data.slot_date < date.today(): raise HTTPException(status_code=400, detail="Slot date cannot be in the past")
    slot = TimeSlot(**data.model_dump()); db.add(slot); db.commit(); db.refresh(slot); return slot

@app.get("/api/packages/{package_id}/slots", response_model=List[TimeSlotResponse])
def list_slots(package_id: int, slot_date: date | None = None, db: Session = Depends(get_db)):
    query = db.query(TimeSlot).filter(TimeSlot.package_id == package_id, TimeSlot.is_available.is_(True), TimeSlot.slot_date >= date.today())
    if slot_date: query = query.filter(TimeSlot.slot_date == slot_date)
    return query.order_by(TimeSlot.slot_date, TimeSlot.slot_time).all()

@app.post("/api/bookings", response_model=BookingResponse, status_code=201)
def create_booking(data: BookingCreate, email: str = Depends(verify_token), db: Session = Depends(get_db)):
    user = current_user(email, db)
    package = db.query(Package).filter(Package.id == data.package_id, Package.is_active.is_(True)).first()
    slot = db.query(TimeSlot).filter(TimeSlot.id == data.time_slot_id, TimeSlot.package_id == data.package_id).first()
    if not package or not slot: raise HTTPException(status_code=404, detail="Package or slot not found")
    if slot.slot_date != data.appointment_date or slot.slot_time != data.appointment_time: raise HTTPException(status_code=400, detail="Appointment does not match selected slot")
    if slot.slot_date < date.today() or not slot.is_available or slot.booked_count >= slot.capacity: raise HTTPException(status_code=409, detail="This slot is no longer available")
    slot.booked_count += 1
    if slot.booked_count >= slot.capacity: slot.is_available = False
    booking = Booking(user_id=user.id, package_id=package.id, time_slot_id=slot.id, appointment_date=slot.slot_date, appointment_time=slot.slot_time, status="pending", token_number=f"CQ-{secrets.token_hex(3).upper()}", notes=data.notes)
    db.add(booking); db.commit(); db.refresh(booking); return booking

@app.get("/api/bookings", response_model=List[BookingDetailResponse])
def my_bookings(email: str = Depends(verify_token), db: Session = Depends(get_db)):
    user = current_user(email, db)
    bookings = db.query(Booking).options(joinedload(Booking.patient), joinedload(Booking.package)).filter(Booking.user_id == user.id).order_by(Booking.appointment_date.desc(), Booking.appointment_time.desc()).all()
    return [booking_detail(b) for b in bookings]

@app.put("/api/bookings/{booking_id}", response_model=BookingResponse)
def update_booking(booking_id: int, data: BookingUpdate, email: str = Depends(verify_token), db: Session = Depends(get_db)):
    user = current_user(email, db); booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking: raise HTTPException(status_code=404, detail="Booking not found")
    if booking.user_id != user.id and user.role not in {"admin", "staff", "doctor"}: raise HTTPException(status_code=403, detail="Not authorized")
    if data.status == "cancelled":
        raise HTTPException(status_code=400, detail="Use the cancellation endpoint to cancel a booking")
    if data.status and data.status not in {"pending", "confirmed", "completed"}: raise HTTPException(status_code=400, detail="Invalid booking status")
    old_status = booking.status
    for key, value in data.model_dump(exclude_unset=True).items(): setattr(booking, key, value)
    db.commit(); db.refresh(booking); return booking

@app.post("/api/bookings/{booking_id}/cancel", response_model=BookingDetailResponse)
def cancel_booking(booking_id: int, data: CancellationRequest | None = None, email: str = Depends(verify_token), db: Session = Depends(get_db)):
    user = current_user(email, db)
    booking = db.query(Booking).options(joinedload(Booking.patient), joinedload(Booking.package), joinedload(Booking.time_slot), joinedload(Booking.cancellations)).filter(Booking.id == booking_id).first()
    if not booking: raise HTTPException(status_code=404, detail="Booking not found")
    if booking.user_id != user.id and user.role not in {"admin", "staff", "doctor"}:
        raise HTTPException(status_code=403, detail="You can only cancel your own bookings")
    if booking.status == "cancelled":
        raise HTTPException(status_code=409, detail="Booking is already cancelled")
    if booking.status == "completed":
        raise HTTPException(status_code=400, detail="Completed bookings cannot be cancelled")

    previous_status = booking.status
    booking.status = "cancelled"
    if booking.time_slot:
        booking.time_slot.booked_count = max(0, booking.time_slot.booked_count - 1)
        booking.time_slot.is_available = True
    if booking.payment:
        booking.payment.payment_status = "cancelled"
        booking.payment.notes = (booking.payment.notes + " | Booking cancelled") if booking.payment.notes else "Booking cancelled"
    cancellation = BookingCancellation(booking_id=booking.id, cancelled_by_user_id=user.id, previous_status=previous_status, reason=data.reason if data else None)
    db.add(cancellation)
    db.commit()
    db.refresh(booking)
    return booking_detail(booking)

@app.get("/api/bookings/{booking_id}/cancellations", response_model=List[CancellationResponse])
def booking_cancellations(booking_id: int, email: str = Depends(verify_token), db: Session = Depends(get_db)):
    user = current_user(email, db)
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking: raise HTTPException(status_code=404, detail="Booking not found")
    if booking.user_id != user.id and user.role not in {"admin", "staff", "doctor"}:
        raise HTTPException(status_code=403, detail="Not authorized")
    return db.query(BookingCancellation).filter(BookingCancellation.booking_id == booking_id).order_by(BookingCancellation.cancelled_at.desc()).all()

@app.get("/api/admin/bookings", response_model=List[BookingDetailResponse])
def all_bookings(email: str = Depends(verify_token), db: Session = Depends(get_db)):
    require_roles(current_user(email, db), "admin", "staff")
    bookings = db.query(Booking).options(joinedload(Booking.patient), joinedload(Booking.package)).order_by(Booking.created_at.desc()).all()
    return [booking_detail(b) for b in bookings]

@app.post("/api/payments", response_model=PaymentResponse, status_code=201)
def create_payment(data: PaymentCreate, email: str = Depends(verify_token), db: Session = Depends(get_db)):
    user = current_user(email, db); booking = db.query(Booking).options(joinedload(Booking.package)).filter(Booking.id == data.booking_id, Booking.user_id == user.id).first()
    if not booking: raise HTTPException(status_code=404, detail="Booking not found")
    if abs(data.amount - booking.package.price) > 0.01: raise HTTPException(status_code=400, detail="Payment amount does not match package price")
    if db.query(Payment).filter(Payment.booking_id == booking.id).first(): raise HTTPException(status_code=409, detail="Payment already recorded")
    is_cash = data.payment_method == "cash"
    payment = Payment(user_id=user.id, booking_id=booking.id, amount=booking.package.price, payment_method=data.payment_method, payment_status="pending" if is_cash else "completed", transaction_id=f"CQ-{secrets.token_hex(8).upper()}", reference_id="CASH-DUE" if is_cash else f"MOCK-{secrets.token_hex(6).upper()}", notes=data.notes)
    booking.status = "pending" if is_cash else "confirmed"
    db.add(payment); db.commit(); db.refresh(payment); return payment

@app.post("/api/payments/{payment_id}/verify", response_model=PaymentResponse)
def verify_payment(payment_id: int, email: str = Depends(verify_token), db: Session = Depends(get_db)):
    user = current_user(email, db); payment = db.query(Payment).filter(Payment.id == payment_id, Payment.user_id == user.id).first()
    if not payment: raise HTTPException(status_code=404, detail="Payment not found")
    if payment.payment_method == "cash": return payment
    payment.payment_status = "completed"
    if payment.booking: payment.booking.status = "confirmed"
    db.commit(); db.refresh(payment); return payment

@app.get("/api/payments", response_model=List[PaymentResponse])
def my_payments(email: str = Depends(verify_token), db: Session = Depends(get_db)):
    return db.query(Payment).filter(Payment.user_id == current_user(email, db).id).order_by(Payment.created_at.desc()).all()

@app.get("/api/dashboard", response_model=PatientStats)
def patient_dashboard(email: str = Depends(verify_token), db: Session = Depends(get_db)):
    user = current_user(email, db); bookings = db.query(Booking).options(joinedload(Booking.patient), joinedload(Booking.package)).filter(Booking.user_id == user.id).order_by(Booking.created_at.desc()).all(); payments = db.query(Payment).filter(Payment.user_id == user.id, Payment.payment_status == "completed").all()
    return {"total_bookings": len(bookings), "completed_bookings": sum(b.status == "completed" for b in bookings), "pending_bookings": sum(b.status in {"pending", "confirmed"} for b in bookings), "total_spent": sum(p.amount for p in payments), "recent_bookings": [booking_detail(b) for b in bookings[:5]]}

@app.get("/api/admin/dashboard", response_model=DashboardStats)
def admin_dashboard(email: str = Depends(verify_token), db: Session = Depends(get_db)):
    require_roles(current_user(email, db), "admin", "staff")
    bookings = db.query(Booking).all(); payments = db.query(Payment).filter(Payment.payment_status == "completed").all()
    return {"total_patients": db.query(User).filter(User.role == "patient").count(), "total_bookings": len(bookings), "pending_bookings": sum(b.status in {"pending", "confirmed"} for b in bookings), "completed_bookings": sum(b.status == "completed" for b in bookings), "total_revenue": sum(p.amount for p in payments), "total_packages": db.query(Package).filter(Package.is_active.is_(True)).count()}

@app.get("/api/doctor/dashboard")
def doctor_dashboard(email: str = Depends(verify_token), db: Session = Depends(get_db)):
    user = current_user(email, db); require_roles(user, "doctor", "staff", "admin")
    bookings = db.query(Booking).options(joinedload(Booking.patient), joinedload(Booking.package), joinedload(Booking.cancellations)).order_by(Booking.appointment_date, Booking.appointment_time).all()
    return {"doctor": user, "appointments": [{"id": b.id, "patient": UserResponse.model_validate(b.patient), "package": PackageResponse.model_validate(b.package), "appointment_date": b.appointment_date, "appointment_time": b.appointment_time, "status": b.status, "token_number": b.token_number, "cancellations": [CancellationResponse.model_validate(c) for c in b.cancellations]} for b in bookings]}

@app.get("/api/doctor/appointments")
def doctor_appointments(email: str = Depends(verify_token), db: Session = Depends(get_db)):
    return doctor_dashboard(email, db)["appointments"]
