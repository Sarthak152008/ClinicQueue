from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text, Time, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

# ==================== USER MODELS ====================

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(15), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), default="patient")  # patient, doctor, admin, staff
    is_active = Column(Boolean, default=True)
    gender = Column(String(20))
    age = Column(Integer)
    address = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    bookings = relationship("Booking", back_populates="patient")
    payments = relationship("Payment", back_populates="user")
    doctor = relationship("Doctor", back_populates="user", uselist=False)
    cancellations = relationship("BookingCancellation", back_populates="cancelled_by")

class Doctor(Base):
    __tablename__ = "doctors"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    specialization = Column(String(255))
    experience_years = Column(Integer)
    registration_number = Column(String(100), unique=True)
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="doctor")
    appointments = relationship("Appointment", back_populates="doctor")

# ==================== PACKAGE/TEST MODELS ====================

class Package(Base):
    __tablename__ = "packages"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    category = Column(String(100))  # Basic, Advanced, Full Body, etc.
    tests_count = Column(Integer, default=1)
    includes_tests = Column(Text)  # JSON list of tests
    preparation_instructions = Column(Text)
    report_time = Column(String(100))  # e.g., "24 hours"
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    bookings = relationship("Booking", back_populates="package")
    slots = relationship("TimeSlot", back_populates="package")

class TimeSlot(Base):
    __tablename__ = "time_slots"
    
    id = Column(Integer, primary_key=True, index=True)
    package_id = Column(Integer, ForeignKey("packages.id"), nullable=False)
    slot_date = Column(Date, nullable=False)
    slot_time = Column(Time, nullable=False)
    capacity = Column(Integer, default=10)  # Max patients per slot
    booked_count = Column(Integer, default=0)
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    package = relationship("Package", back_populates="slots")
    bookings = relationship("Booking", back_populates="time_slot")

# ==================== BOOKING MODELS ====================

class Booking(Base):
    __tablename__ = "bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    package_id = Column(Integer, ForeignKey("packages.id"), nullable=False)
    time_slot_id = Column(Integer, ForeignKey("time_slots.id"))
    booking_date = Column(DateTime, default=datetime.utcnow)
    appointment_date = Column(Date)
    appointment_time = Column(Time)
    status = Column(String(50), default="pending")  # pending, confirmed, completed, cancelled
    token_number = Column(String(20))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    patient = relationship("User", back_populates="bookings")
    package = relationship("Package", back_populates="bookings")
    time_slot = relationship("TimeSlot", back_populates="bookings")
    payment = relationship("Payment", uselist=False, back_populates="booking")
    cancellations = relationship("BookingCancellation", back_populates="booking", cascade="all, delete-orphan")

class BookingCancellation(Base):
    __tablename__ = "booking_cancellations"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=False, index=True)
    cancelled_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reason = Column(Text)
    previous_status = Column(String(50), nullable=False)
    cancelled_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    booking = relationship("Booking", back_populates="cancellations")
    cancelled_by = relationship("User", back_populates="cancellations")

class Appointment(Base):
    __tablename__ = "appointments"
    
    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    appointment_date = Column(Date, nullable=False)
    appointment_time = Column(Time, nullable=False)
    status = Column(String(50), default="pending")  # pending, completed, cancelled
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    doctor = relationship("Doctor", back_populates="appointments")
    patient = relationship("User")

# ==================== PAYMENT MODELS ====================

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    booking_id = Column(Integer, ForeignKey("bookings.id"))
    amount = Column(Float, nullable=False)
    payment_method = Column(String(50))  # card, upi, net_banking, cash
    payment_status = Column(String(50), default="pending")  # pending, completed, failed
    transaction_id = Column(String(100), unique=True)
    reference_id = Column(String(100))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="payments")
    booking = relationship("Booking", back_populates="payment")

# ==================== ADMIN MODELS ====================

class SystemLog(Base):
    __tablename__ = "system_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    action = Column(String(255))
    performed_by = Column(Integer, ForeignKey("users.id"))
    resource_type = Column(String(100))  # User, Booking, Payment, etc.
    resource_id = Column(Integer)
    details = Column(Text)
    ip_address = Column(String(45))
    timestamp = Column(DateTime, default=datetime.utcnow)
