"""SQLAlchemy data layer for the Integrated Patient Care Management System."""

from __future__ import annotations

import hashlib
import logging
import random
from datetime import date, datetime, timedelta
from pathlib import Path

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
    func,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

DB_DIR = Path("data")
DB_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DB_DIR / "ipcms.db"

engine = create_engine(
    f"sqlite:///{DB_PATH}",
    echo=False,
    future=True,
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, future=True)
Base = declarative_base()


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    full_name = Column(String(120), nullable=False)
    role = Column(String(40), default="admin", nullable=False)
    password_hash = Column(String(256), nullable=False)
    specialization = Column(String(120), default="")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Patient(Base):
    __tablename__ = "patients"
    id = Column(Integer, primary_key=True)
    mrn = Column(String(20), unique=True, nullable=False)
    first_name = Column(String(80), nullable=False)
    last_name = Column(String(80), nullable=False)
    gender = Column(String(10), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    blood_group = Column(String(5), default="")
    phone = Column(String(30), default="")
    email = Column(String(120), default="")
    address = Column(String(255), default="")
    emergency_contact = Column(String(120), default="")
    registered_on = Column(DateTime, default=datetime.utcnow)

    consultations = relationship("Consultation", back_populates="patient")
    prescriptions = relationship("Prescription", back_populates="patient")


class Consultation(Base):
    __tablename__ = "consultations"
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    visit_date = Column(DateTime, default=datetime.utcnow)
    chief_complaint = Column(String(255), default="")
    diagnosis = Column(String(255), default="")
    notes = Column(Text, default="")
    status = Column(String(30), default="Completed")

    patient = relationship("Patient", back_populates="consultations")
    doctor = relationship("User")


class Prescription(Base):
    __tablename__ = "prescriptions"
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    consultation_id = Column(
        Integer, ForeignKey("consultations.id"), nullable=True
    )
    issued_on = Column(DateTime, default=datetime.utcnow)
    medication = Column(String(120), nullable=False)
    dosage = Column(String(80), default="")
    frequency = Column(String(80), default="")
    duration = Column(String(80), default="")
    instructions = Column(Text, default="")
    status = Column(String(30), default="Active")

    patient = relationship("Patient", back_populates="prescriptions")
    doctor = relationship("User")


class LaboratoryReport(Base):
    __tablename__ = "laboratory_reports"
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    test_name = Column(String(120), nullable=False)
    test_type = Column(String(60), default="Hematology")
    result = Column(String(120), default="")
    reference_range = Column(String(120), default="")
    status = Column(String(30), default="Completed")
    performed_on = Column(DateTime, default=datetime.utcnow)


class MedicalHistory(Base):
    __tablename__ = "medical_history"
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    condition = Column(String(120), nullable=False)
    onset_date = Column(Date, default=date.today)
    notes = Column(Text, default="")


class Allergy(Base):
    __tablename__ = "allergies"
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    allergen = Column(String(120), nullable=False)
    severity = Column(String(30), default="Mild")
    reaction = Column(String(255), default="")


class DiagnosisHistory(Base):
    __tablename__ = "diagnosis_history"
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    diagnosis = Column(String(255), nullable=False)
    diagnosed_on = Column(Date, default=date.today)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=True)


class Medication(Base):
    __tablename__ = "medications"
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    name = Column(String(120), nullable=False)
    dosage = Column(String(80), default="")
    started_on = Column(Date, default=date.today)
    active = Column(Boolean, default=True)


class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    title = Column(String(200), nullable=False)
    doc_type = Column(String(60), default="Report")
    uploaded_on = Column(DateTime, default=datetime.utcnow)
    file_path = Column(String(255), default="")


class Setting(Base):
    __tablename__ = "settings"
    id = Column(Integer, primary_key=True)
    key = Column(String(80), unique=True, nullable=False)
    value = Column(Text, default="")


class MedicalSummary(Base):
    __tablename__ = "medical_summaries"
    id = Column(Integer, primary_key=True)
    patient_id = Column(
        Integer, ForeignKey("patients.id"), unique=True, nullable=False
    )
    height_cm = Column(String(20), default="")
    weight_kg = Column(String(20), default="")
    bmi = Column(String(20), default="")
    smoking = Column(String(20), default="No")
    alcohol = Column(String(20), default="No")
    chronic_diseases = Column(Text, default="")
    remarks = Column(Text, default="")
    updated_on = Column(DateTime, default=datetime.utcnow)


class ReportLog(Base):
    __tablename__ = "report_logs"
    id = Column(Integer, primary_key=True)
    kind = Column(String(60), nullable=False)
    generated_on = Column(DateTime, default=datetime.utcnow)
    generated_by = Column(String(80), default="admin")


def init_db() -> None:
    try:
        Base.metadata.create_all(engine)
        _seed_if_empty()
    except Exception as e:
        logging.exception(f"Error initializing database: {e}")


# ---------------------------------------------------------------------------
# Seeding
# ---------------------------------------------------------------------------

FIRST_NAMES = [
    "James",
    "Mary",
    "John",
    "Patricia",
    "Robert",
    "Jennifer",
    "Michael",
    "Linda",
    "William",
    "Elizabeth",
    "David",
    "Barbara",
    "Richard",
    "Susan",
    "Joseph",
    "Jessica",
    "Thomas",
    "Sarah",
    "Charles",
    "Karen",
    "Daniel",
    "Nancy",
    "Matthew",
    "Lisa",
    "Anthony",
    "Betty",
    "Ahmed",
    "Fatima",
    "Wei",
    "Aisha",
    "Carlos",
    "Priya",
    "Kenji",
    "Olivia",
    "Noah",
    "Emma",
    "Liam",
    "Ava",
    "Ethan",
    "Sophia",
    "Mason",
    "Isabella",
    "Logan",
    "Mia",
    "Lucas",
    "Charlotte",
    "Jackson",
    "Amelia",
    "Henry",
    "Harper",
]
LAST_NAMES = [
    "Smith",
    "Johnson",
    "Williams",
    "Brown",
    "Jones",
    "Garcia",
    "Miller",
    "Davis",
    "Rodriguez",
    "Martinez",
    "Hernandez",
    "Lopez",
    "Gonzalez",
    "Wilson",
    "Anderson",
    "Thomas",
    "Taylor",
    "Moore",
    "Jackson",
    "Martin",
    "Lee",
    "Perez",
    "Thompson",
    "White",
    "Harris",
    "Sanchez",
    "Clark",
    "Ramirez",
    "Lewis",
    "Robinson",
    "Walker",
    "Young",
    "Allen",
    "King",
    "Wright",
    "Scott",
    "Torres",
    "Nguyen",
    "Hill",
    "Flores",
    "Green",
    "Adams",
    "Nelson",
    "Baker",
    "Hall",
    "Rivera",
    "Campbell",
    "Mitchell",
    "Carter",
    "Roberts",
]
BLOOD = ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]
SPECIALIZATIONS = [
    "General Medicine",
    "Cardiology",
    "Pediatrics",
    "Orthopedics",
    "Neurology",
    "Dermatology",
    "Oncology",
    "Radiology",
    "Psychiatry",
    "Endocrinology",
]
COMPLAINTS = [
    "Persistent cough",
    "Chest pain",
    "Severe headache",
    "High fever",
    "Abdominal pain",
    "Shortness of breath",
    "Back pain",
    "Skin rash",
    "Fatigue",
    "Dizziness",
    "Joint pain",
    "Nausea and vomiting",
]
DIAGNOSES = [
    "Hypertension",
    "Type 2 Diabetes",
    "Acute Bronchitis",
    "Migraine",
    "Gastritis",
    "Anemia",
    "Asthma",
    "Sinusitis",
    "Arthritis",
    "Urinary Tract Infection",
    "Hyperlipidemia",
    "Anxiety Disorder",
]
MEDS = [
    ("Amoxicillin", "500mg"),
    ("Metformin", "850mg"),
    ("Lisinopril", "10mg"),
    ("Atorvastatin", "20mg"),
    ("Ibuprofen", "400mg"),
    ("Omeprazole", "20mg"),
    ("Salbutamol", "100mcg"),
    ("Paracetamol", "500mg"),
    ("Cetirizine", "10mg"),
    ("Losartan", "50mg"),
    ("Aspirin", "75mg"),
    ("Levothyroxine", "50mcg"),
]
FREQUENCIES = [
    "Once daily",
    "Twice daily",
    "Three times daily",
    "Every 8 hours",
    "As needed",
]
DURATIONS = ["5 days", "7 days", "10 days", "14 days", "1 month", "3 months"]
LAB_TESTS = [
    ("Complete Blood Count", "Hematology"),
    ("Lipid Panel", "Biochemistry"),
    ("Blood Glucose", "Biochemistry"),
    ("Thyroid Function", "Endocrinology"),
    ("Urinalysis", "Urinology"),
    ("Liver Function Test", "Biochemistry"),
    ("Kidney Function Test", "Biochemistry"),
    ("HbA1c", "Endocrinology"),
    ("Chest X-Ray", "Radiology"),
    ("ECG", "Cardiology"),
]
LAB_STATUS = ["Completed", "Pending", "In Progress"]
ALLERGENS = [
    "Penicillin",
    "Peanuts",
    "Latex",
    "Pollen",
    "Dust Mites",
    "Shellfish",
    "Sulfa Drugs",
]
CONDITIONS = [
    "Hypertension",
    "Diabetes",
    "Asthma",
    "Migraine",
    "Arthritis",
    "Hyperthyroidism",
]


def _seed_if_empty() -> None:
    with SessionLocal() as db:
        if db.query(User).count() > 0:
            return

        # 1 Admin + 10 doctors
        admin = User(
            username="admin",
            email="admin@ipcms.local",
            full_name="System Administrator",
            role="admin",
            password_hash=hash_password("admin123"),
        )
        db.add(admin)

        doctors: list[User] = []
        for i in range(10):
            fn = random.choice(FIRST_NAMES)
            ln = random.choice(LAST_NAMES)
            doc = User(
                username=f"dr_{fn.lower()}{i}",
                email=f"{fn.lower()}.{ln.lower()}@ipcms.local",
                full_name=f"Dr. {fn} {ln}",
                role="doctor",
                specialization=random.choice(SPECIALIZATIONS),
                password_hash=hash_password("doctor123"),
            )
            doctors.append(doc)
            db.add(doc)
        db.flush()

        # 50 Patients
        patients: list[Patient] = []
        for i in range(50):
            fn = random.choice(FIRST_NAMES)
            ln = random.choice(LAST_NAMES)
            dob = date.today() - timedelta(
                days=random.randint(365 * 5, 365 * 85)
            )
            reg = datetime.utcnow() - timedelta(days=random.randint(1, 365))
            p = Patient(
                mrn=f"MRN{10000 + i}",
                first_name=fn,
                last_name=ln,
                gender=random.choice(["Male", "Female"]),
                date_of_birth=dob,
                blood_group=random.choice(BLOOD),
                phone=f"+1-555-{random.randint(1000, 9999)}",
                email=f"{fn.lower()}.{ln.lower()}{i}@example.com",
                address=f"{random.randint(1, 999)} Main St, City",
                emergency_contact=f"+1-555-{random.randint(1000, 9999)}",
                registered_on=reg,
            )
            patients.append(p)
            db.add(p)
        db.flush()

        # 100 Consultations
        consultations: list[Consultation] = []
        for _ in range(100):
            c = Consultation(
                patient_id=random.choice(patients).id,
                doctor_id=random.choice(doctors).id,
                visit_date=datetime.utcnow()
                - timedelta(days=random.randint(0, 180)),
                chief_complaint=random.choice(COMPLAINTS),
                diagnosis=random.choice(DIAGNOSES),
                notes="Patient advised follow-up in 2 weeks.",
                status=random.choice(
                    ["Completed", "Completed", "Completed", "Follow-up"]
                ),
            )
            consultations.append(c)
            db.add(c)
        db.flush()

        # 100 Prescriptions
        for _ in range(100):
            med, dose = random.choice(MEDS)
            c = random.choice(consultations)
            db.add(
                Prescription(
                    patient_id=c.patient_id,
                    doctor_id=c.doctor_id,
                    consultation_id=c.id,
                    issued_on=c.visit_date,
                    medication=med,
                    dosage=dose,
                    frequency=random.choice(FREQUENCIES),
                    duration=random.choice(DURATIONS),
                    instructions="Take with food.",
                    status=random.choice(["Active", "Active", "Completed"]),
                )
            )

        # 80 Lab reports
        for _ in range(80):
            name, ttype = random.choice(LAB_TESTS)
            p = random.choice(patients)
            db.add(
                LaboratoryReport(
                    patient_id=p.id,
                    doctor_id=random.choice(doctors).id,
                    test_name=name,
                    test_type=ttype,
                    result=f"{random.uniform(0.8, 12.5):.2f}",
                    reference_range="Normal",
                    status=random.choice(LAB_STATUS),
                    performed_on=datetime.utcnow()
                    - timedelta(days=random.randint(0, 180)),
                )
            )

        # Medical history / allergies / diagnosis / medications / documents
        for p in patients:
            for _ in range(random.randint(1, 3)):
                db.add(
                    MedicalHistory(
                        patient_id=p.id,
                        condition=random.choice(CONDITIONS),
                        onset_date=date.today()
                        - timedelta(days=random.randint(30, 3000)),
                        notes="Managed with medication.",
                    )
                )
            for _ in range(random.randint(0, 2)):
                db.add(
                    Allergy(
                        patient_id=p.id,
                        allergen=random.choice(ALLERGENS),
                        severity=random.choice(["Mild", "Moderate", "Severe"]),
                        reaction="Rash / itching",
                    )
                )
            for _ in range(random.randint(1, 2)):
                db.add(
                    DiagnosisHistory(
                        patient_id=p.id,
                        diagnosis=random.choice(DIAGNOSES),
                        diagnosed_on=date.today()
                        - timedelta(days=random.randint(1, 1000)),
                        doctor_id=random.choice(doctors).id,
                    )
                )
            for _ in range(random.randint(0, 2)):
                med, dose = random.choice(MEDS)
                db.add(
                    Medication(
                        patient_id=p.id,
                        name=med,
                        dosage=dose,
                        started_on=date.today()
                        - timedelta(days=random.randint(1, 500)),
                        active=random.choice([True, True, False]),
                    )
                )
            if random.random() < 0.4:
                db.add(
                    Document(
                        patient_id=p.id,
                        title=f"Report_{p.mrn}.pdf",
                        doc_type=random.choice(["Lab", "Imaging", "Discharge"]),
                        uploaded_on=datetime.utcnow()
                        - timedelta(days=random.randint(1, 200)),
                        file_path="",
                    )
                )

        # Report logs
        for _ in range(35):
            db.add(
                ReportLog(
                    kind=random.choice(
                        [
                            "Prescription",
                            "Lab",
                            "Medical History",
                            "Patient Summary",
                        ]
                    ),
                    generated_on=datetime.utcnow()
                    - timedelta(days=random.randint(0, 180)),
                    generated_by="admin",
                )
            )

        # Settings
        for k, v in [
            ("hospital_name", "St. Mary's Integrated Care"),
            ("hospital_address", "123 Wellness Blvd, Springfield"),
            ("contact_email", "contact@ipcms.local"),
            ("contact_phone", "+1-555-0100"),
            ("timezone", "UTC"),
            ("theme", "light"),
        ]:
            db.add(Setting(key=k, value=v))

        db.commit()


# Initialize at import so state modules can query immediately.
init_db()
