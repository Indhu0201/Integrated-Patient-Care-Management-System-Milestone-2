import logging
from datetime import datetime, timedelta
from typing import TypedDict

import reflex as rx
from sqlalchemy import func

from app.database import (
    Consultation,
    LaboratoryReport,
    MedicalHistory,
    Patient,
    Prescription,
    ReportLog,
    SessionLocal,
    User,
)


class RecentConsultation(TypedDict):
    id: int
    patient: str
    doctor: str
    diagnosis: str
    date: str
    status: str


class RecentPrescription(TypedDict):
    id: int
    patient: str
    medication: str
    dosage: str
    date: str
    status: str


class RecentLab(TypedDict):
    id: int
    patient: str
    test: str
    result: str
    date: str
    status: str


class HistorySummary(TypedDict):
    patient: str
    condition: str
    onset: str


class MonthlyPoint(TypedDict):
    month: str
    count: int


class NamedCount(TypedDict):
    name: str
    count: int


class DashboardState(rx.State):
    loading: bool = True

    # KPIs
    total_patients: int = 0
    total_consultations: int = 0
    total_prescriptions: int = 0
    total_lab_tests: int = 0
    total_reports: int = 0
    total_doctors: int = 0

    # Recent sections
    recent_consultations: list[RecentConsultation] = []
    recent_prescriptions: list[RecentPrescription] = []
    recent_labs: list[RecentLab] = []
    history_summary: list[HistorySummary] = []

    # Charts
    monthly_consultations: list[MonthlyPoint] = []
    prescription_stats: list[NamedCount] = []
    lab_stats: list[NamedCount] = []
    patient_growth: list[MonthlyPoint] = []

    # System status
    db_status: str = "Online"
    last_updated: str = ""

    # Search
    search_query: str = ""
    search_results: list[dict[str, str]] = []

    @rx.event
    def load_dashboard(self):
        self.loading = True
        try:
            with SessionLocal() as db:
                self.total_patients = (
                    db.query(func.count(Patient.id)).scalar() or 0
                )
                self.total_consultations = (
                    db.query(func.count(Consultation.id)).scalar() or 0
                )
                self.total_prescriptions = (
                    db.query(func.count(Prescription.id)).scalar() or 0
                )
                self.total_lab_tests = (
                    db.query(func.count(LaboratoryReport.id)).scalar() or 0
                )
                self.total_reports = (
                    db.query(func.count(ReportLog.id)).scalar() or 0
                )
                self.total_doctors = (
                    db.query(func.count(User.id))
                    .filter(User.role == "doctor")
                    .scalar()
                    or 0
                )

                # Recent Consultations (last 8)
                rows = (
                    db.query(Consultation, Patient, User)
                    .join(Patient, Consultation.patient_id == Patient.id)
                    .join(User, Consultation.doctor_id == User.id)
                    .order_by(Consultation.visit_date.desc())
                    .limit(8)
                    .all()
                )
                self.recent_consultations = [
                    {
                        "id": c.id,
                        "patient": f"{p.first_name} {p.last_name}",
                        "doctor": u.full_name,
                        "diagnosis": c.diagnosis,
                        "date": c.visit_date.strftime("%Y-%m-%d"),
                        "status": c.status,
                    }
                    for c, p, u in rows
                ]

                # Recent Prescriptions
                rx_rows = (
                    db.query(Prescription, Patient)
                    .join(Patient, Prescription.patient_id == Patient.id)
                    .order_by(Prescription.issued_on.desc())
                    .limit(8)
                    .all()
                )
                self.recent_prescriptions = [
                    {
                        "id": pr.id,
                        "patient": f"{p.first_name} {p.last_name}",
                        "medication": pr.medication,
                        "dosage": pr.dosage,
                        "date": pr.issued_on.strftime("%Y-%m-%d"),
                        "status": pr.status,
                    }
                    for pr, p in rx_rows
                ]

                # Recent Labs
                lab_rows = (
                    db.query(LaboratoryReport, Patient)
                    .join(Patient, LaboratoryReport.patient_id == Patient.id)
                    .order_by(LaboratoryReport.performed_on.desc())
                    .limit(8)
                    .all()
                )
                self.recent_labs = [
                    {
                        "id": l.id,
                        "patient": f"{p.first_name} {p.last_name}",
                        "test": l.test_name,
                        "result": l.result,
                        "date": l.performed_on.strftime("%Y-%m-%d"),
                        "status": l.status,
                    }
                    for l, p in lab_rows
                ]

                # Medical history summary
                hist_rows = (
                    db.query(MedicalHistory, Patient)
                    .join(Patient, MedicalHistory.patient_id == Patient.id)
                    .order_by(MedicalHistory.id.desc())
                    .limit(6)
                    .all()
                )
                self.history_summary = [
                    {
                        "patient": f"{p.first_name} {p.last_name}",
                        "condition": m.condition,
                        "onset": m.onset_date.strftime("%Y-%m-%d"),
                    }
                    for m, p in hist_rows
                ]

                # Monthly Consultations (last 6 months)
                self.monthly_consultations = self._monthly(
                    db, Consultation, Consultation.visit_date
                )
                self.patient_growth = self._monthly(
                    db, Patient, Patient.registered_on
                )

                # Prescription stats by medication
                pres_stats = (
                    db.query(
                        Prescription.medication, func.count(Prescription.id)
                    )
                    .group_by(Prescription.medication)
                    .order_by(func.count(Prescription.id).desc())
                    .limit(6)
                    .all()
                )
                self.prescription_stats = [
                    {"name": m, "count": int(c)} for m, c in pres_stats
                ]

                # Lab stats by type
                lab_stats = (
                    db.query(
                        LaboratoryReport.test_type,
                        func.count(LaboratoryReport.id),
                    )
                    .group_by(LaboratoryReport.test_type)
                    .order_by(func.count(LaboratoryReport.id).desc())
                    .all()
                )
                self.lab_stats = [
                    {"name": t, "count": int(c)} for t, c in lab_stats
                ]

            self.last_updated = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
            self.db_status = "Online"
        except Exception as e:
            logging.exception(f"Dashboard load error: {e}")
            self.db_status = "Error"
        finally:
            self.loading = False

    def _monthly(self, db, model, date_col) -> list[MonthlyPoint]:
        result: list[MonthlyPoint] = []
        now = datetime.utcnow().replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )
        for i in range(5, -1, -1):
            year = now.year
            month = now.month - i
            while month <= 0:
                month += 12
                year -= 1
            start = datetime(year, month, 1)
            if month == 12:
                end = datetime(year + 1, 1, 1)
            else:
                end = datetime(year, month + 1, 1)
            count = (
                db.query(func.count(model.id))
                .filter(date_col >= start, date_col < end)
                .scalar()
                or 0
            )
            result.append({"month": start.strftime("%b"), "count": int(count)})
        return result

    @rx.event
    def set_search_query(self, value: str):
        self.search_query = value

    @rx.event
    def run_search(self):
        q = self.search_query.strip()
        if not q:
            self.search_results = []
            return
        try:
            with SessionLocal() as db:
                like = f"%{q}%"
                pats = (
                    db.query(Patient)
                    .filter(
                        (Patient.first_name.ilike(like))
                        | (Patient.last_name.ilike(like))
                        | (Patient.mrn.ilike(like))
                    )
                    .limit(10)
                    .all()
                )
                self.search_results = [
                    {
                        "kind": "Patient",
                        "title": f"{p.first_name} {p.last_name}",
                        "subtitle": f"MRN {p.mrn} • {p.gender} • {p.blood_group}",
                    }
                    for p in pats
                ]
        except Exception as e:
            logging.exception(f"Search error: {e}")
            self.search_results = []
