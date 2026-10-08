from datetime import date, time, timedelta
from database import SessionLocal, init_db
from models import Doctor, Package, TimeSlot, User
from auth import hash_password

PACKAGES = [
    ("Complete Blood Check", "CBC, blood group, hemoglobin, WBC and RBC screening.", 799, "Basic Screening", 5, "CBC, Blood Group, Hemoglobin, WBC, RBC", None, "24 hours"),
    ("Liver Function Test", "A focused panel for liver health and enzyme levels.", 1299, "Organ Tests", 5, "LFT, Bilirubin, SGOT, SGPT, Protein", "Avoid alcohol for 24 hours.", "24 hours"),
    ("Fever Screening", "A fast infection screening panel for common fever causes.", 999, "Infection Screening", 5, "CBC, CRP, Dengue, Typhoid, Malaria", None, "24 hours"),
    ("Diabetes Checkup", "A complete snapshot of blood sugar and metabolic health.", 899, "Chronic Disease", 4, "HbA1c, Fasting Sugar, PP Sugar, Lipid Profile", "Fast for 8–12 hours.", "24 hours"),
    ("Thyroid Profile", "T3, T4 and TSH for complete thyroid function testing.", 1199, "Hormone Tests", 3, "T3, T4, TSH", None, "24 hours"),
    ("Kidney Function", "Kidney health panel including filtration markers.", 1399, "Organ Tests", 4, "Creatinine, BUN, Electrolytes, Uric Acid", None, "24 hours"),
    ("Vitamin D Test", "25-Hydroxy Vitamin D level analysis.", 599, "Vitamin Tests", 1, "Vitamin D", None, "24 hours"),
    ("Vitamin B12 Test", "Vitamin B12 level analysis.", 699, "Vitamin Tests", 1, "Vitamin B12", None, "24 hours"),
    ("Cancer Screening", "A tumor marker panel for proactive screening.", 2499, "Advanced Screening", 5, "PSA, CEA, CA-19-9", "Fasting required.", "48 hours"),
    ("Heart Health", "Lipid, troponin, ECG and glucose screening.", 1999, "Cardio Tests", 4, "Lipid Profile, Troponin, ECG, Glucose", None, "24 hours"),
    ("Comprehensive Health", "Our most complete full-body preventive checkup.", 3999, "Full Body", 15, "CBC, LFT, KFT, Lipids, Glucose, Thyroid", "Fast for 12 hours.", "48 hours"),
    ("COVID-19 Antibody", "IgG and IgM antibody testing.", 799, "Infection", 2, "IgG, IgM", None, "24 hours"),
]

def user(db, email, name, password, role, phone):
    existing = db.query(User).filter(User.email == email).first()
    if existing: return existing
    item = User(name=name, email=email, phone=phone, password_hash=hash_password(password), role=role, age=35, gender="Prefer not to say", address="ClinicQueue Demo Campus")
    db.add(item); db.flush(); return item

def seed():
    init_db(); db = SessionLocal()
    try:
        user(db, "demo@clinicqueue.com", "Demo Patient", "demo123456", "patient", "9876543210")
        user(db, "john@clinicqueue.com", "John Doe", "john123456", "patient", "9123456789")
        user(db, "sarah@clinicqueue.com", "Sarah Smith", "sarah123456", "patient", "9988776655")
        user(db, "admin@clinicqueue.com", "Admin User", "admin123456", "admin", "9000000000")
        doctor_user = user(db, "doctor@clinicqueue.com", "Dr. Rahul Sharma", "doctor123456", "doctor", "9111111111")
        if not db.query(Doctor).filter(Doctor.user_id == doctor_user.id).first(): db.add(Doctor(user_id=doctor_user.id, specialization="General Medicine", experience_years=15, registration_number="REG123456"))
        db.commit()
        if db.query(Package).count() == 0:
            for row in PACKAGES: db.add(Package(name=row[0], description=row[1], price=row[2], category=row[3], tests_count=row[4], includes_tests=row[5], preparation_instructions=row[6], report_time=row[7]))
            db.commit()
        if db.query(TimeSlot).count() == 0:
            for pkg in db.query(Package).all():
                for offset in range(1, 15):
                    for hour in (9, 11, 14, 16): db.add(TimeSlot(package_id=pkg.id, slot_date=date.today() + timedelta(days=offset), slot_time=time(hour, 0), capacity=10, booked_count=0, is_available=True))
            db.commit()
        print("ClinicQueue database seeded successfully")
    finally: db.close()

if __name__ == "__main__": seed()
