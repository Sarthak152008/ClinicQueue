from datetime import date, datetime, time
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

class UserBase(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    email: EmailStr
    phone: str = Field(min_length=7, max_length=20)
    gender: Optional[str] = None
    age: Optional[int] = Field(default=None, ge=0, le=120)
    address: Optional[str] = None

class UserRegister(UserBase):
    password: str = Field(min_length=8, max_length=128)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    role: str
    is_active: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class UserProfileUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=255)
    phone: Optional[str] = Field(default=None, min_length=7, max_length=20)
    gender: Optional[str] = None
    age: Optional[int] = Field(default=None, ge=0, le=120)
    address: Optional[str] = None

class DoctorResponse(BaseModel):
    id: int
    user_id: int
    specialization: Optional[str]
    experience_years: Optional[int]
    registration_number: Optional[str]
    is_available: bool
    model_config = ConfigDict(from_attributes=True)

class PackageCreate(BaseModel):
    name: str = Field(min_length=2)
    description: str = Field(min_length=2)
    price: float = Field(gt=0)
    category: str = Field(min_length=2)
    tests_count: int = Field(ge=1)
    includes_tests: str = Field(min_length=2)
    preparation_instructions: Optional[str] = None
    report_time: Optional[str] = None

class PackageUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = Field(default=None, gt=0)
    category: Optional[str] = None
    tests_count: Optional[int] = Field(default=None, ge=1)
    includes_tests: Optional[str] = None
    preparation_instructions: Optional[str] = None
    report_time: Optional[str] = None
    is_active: Optional[bool] = None

class PackageResponse(PackageCreate):
    id: int
    is_active: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class TimeSlotCreate(BaseModel):
    package_id: int = Field(gt=0)
    slot_date: date
    slot_time: time
    capacity: int = Field(default=10, ge=1, le=100)

class TimeSlotResponse(TimeSlotCreate):
    id: int
    booked_count: int
    is_available: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class BookingCreate(BaseModel):
    package_id: int = Field(gt=0)
    time_slot_id: int = Field(gt=0)
    appointment_date: date
    appointment_time: time
    notes: Optional[str] = None

class BookingUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None
    token_number: Optional[str] = None

class BookingResponse(BaseModel):
    id: int
    user_id: int
    package_id: int
    time_slot_id: Optional[int]
    booking_date: datetime
    appointment_date: Optional[date]
    appointment_time: Optional[time]
    status: str
    token_number: Optional[str]
    notes: Optional[str]
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class BookingDetailResponse(BookingResponse):
    patient: UserResponse
    package: PackageResponse
    cancellations: List["CancellationResponse"] = []
    payment_status: Optional[str] = None

class CancellationRequest(BaseModel):
    reason: Optional[str] = Field(default=None, max_length=1000)

class CancellationResponse(BaseModel):
    id: int
    booking_id: int
    cancelled_by_user_id: int
    reason: Optional[str]
    previous_status: str
    cancelled_at: datetime
    model_config = ConfigDict(from_attributes=True)

class PaymentCreate(BaseModel):
    booking_id: int = Field(gt=0)
    amount: float = Field(gt=0)
    payment_method: str
    notes: Optional[str] = None

    @field_validator("payment_method")
    @classmethod
    def validate_method(cls, value: str) -> str:
        allowed = {"card", "upi", "net_banking", "cash"}
        if value not in allowed:
            raise ValueError(f"payment_method must be one of: {', '.join(sorted(allowed))}")
        return value

class PaymentResponse(BaseModel):
    id: int
    user_id: int
    booking_id: Optional[int]
    amount: float
    payment_method: str
    payment_status: str
    transaction_id: Optional[str]
    reference_id: Optional[str]
    notes: Optional[str]
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse
    role: str

class DashboardStats(BaseModel):
    total_patients: int
    total_bookings: int
    pending_bookings: int
    completed_bookings: int
    total_revenue: float
    total_packages: int

class PatientStats(BaseModel):
    total_bookings: int
    completed_bookings: int
    pending_bookings: int
    total_spent: float
    recent_bookings: List[BookingDetailResponse]
