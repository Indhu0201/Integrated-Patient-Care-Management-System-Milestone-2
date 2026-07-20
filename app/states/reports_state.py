import logging
from datetime import datetime
from typing import TypedDict

import reflex as rx
from sqlalchemy import or_

from app.database import (
    Consultation,
    LaboratoryReport,
    Patient,
    Prescription,
    ReportLog,
    SessionLocal,
    User,
)
from app.states.medical_history_state import EMPTY_PATIENT, PatientInfo, Row
from app.utils.pdf import generate_patient_report_pdf


class PatientHit(TypedDict):
    id: int
    name: str
    mrn: str
    gender: str
    subtitle: str


class ReportsState(rx.State):
    loading: bool = False

    filter_patient_id: str = ""
    filter_patient_name: str = ""
    filter_doctor: str = ""
    filter_diagnosis: str = ""
    filter_date_from: str = ""
    filter_date_to: str = ""

    patient_hits: list[PatientHit] = []
    selected_patient_id: int = 0
    patient_info: PatientInfo = EMPTY_PATIENT
    consultations: list[Row] = []
    prescriptions: list[Row] = []
    labs: list[Row] = []

    generated_pdf: str = ""
    error: str = ""
    success_message: str = ""

    @rx.var
    def has_patient(self) -> bool:
        return self.selected_patient_id != 0

    @rx.event
    def load_page(self):
        self.error = ""
        self.patient_hits = []
        self.selected_patient_id = 0
        self.patient_info = EMPTY_PATIENT

    @rx.event
    def set_filter_patient_id(self, v: str):
        self.filter_patient_id = v

    @rx.event
    def set_filter_patient_name(self, v: str):
        self.filter_patient_name = v

    @rx.event
    def set_filter_doctor(self, v: str):
        self.filter_doctor = v

    @rx.event
    def set_filter_diagnosis(self, v: str):
        self.filter_diagnosis = v

    @rx.event
    def set_filter_date_from(self, v: str):
        self.filter_date_from = v

    @rx.event
    def set_filter_date_to(self, v: str):
        self.filter_date_to = v

    @rx.event
    def clear_filters(self):
        self.filter_patient_id = ""
        self.filter_patient_name = ""
        self.filter_doctor = ""
        self.filter_diagnosis = ""
        self.filter_date_from = ""
        self.filter_date_to = ""
        self.patient_hits = []
        self.selected_patient_id = 0
        self.patient_info = EMPTY_PATIENT

    def _parse_date(self, v: str):
        try:
            return (
                datetime.strptime(v.strip(), "%Y-%m-%d") if v.strip() else None
            )
        except ValueError:
            return None

    @rx.event
    def run_search(self):
        self.error = ""
        date_from = self._parse_date(self.filter_date_from)
        date_to = self._parse_date(self.filter_date_to)
        if self.filter_date_from and date_from is None:
            self.error = "Invalid 'From' date. Use YYYY-MM-DD."
            return
        if self.filter_date_to and date_to is None:
            self.error = "Invalid 'To' date. Use YYYY-MM-DD."
            return
        if date_from and date_to and date_from > date_to:
            self.error = "'From' date must be before 'To' date."
            return
        self.loading = True
        try:
            with SessionLocal() as db:
                q = db.query(Patient).outerjoin(
                    Consultation, Consultation.patient_id == Patient.id
                )
                if self.filter_patient_id.strip():
                    q = q.filter(
                        Patient.mrn.ilike(f"%{self.filter_patient_id.strip()}%")
                    )
                if self.filter_patient_name.strip():
                    like = f"%{self.filter_patient_name.strip()}%"
                    q = q.filter(
                        or_(
                            Patient.first_name.ilike(like),
                            Patient.last_name.ilike(like),
                        )
                    )
                if self.filter_doctor.strip():
                    like = f"%{self.filter_doctor.strip()}%"
                    q = q.join(User, Consultation.doctor_id == User.id).filter(
                        User.full_name.ilike(like)
                    )
                if self.filter_diagnosis.strip():
                    like = f"%{self.filter_diagnosis.strip()}%"
                    q = q.filter(Consultation.diagnosis.ilike(like))
                if date_from:
                    q = q.filter(Consultation.visit_date >= date_from)
                if date_to:
                    q = q.filter(Consultation.visit_date <= date_to)
                q = q.distinct().limit(50)
                rows = q.all()
                self.patient_hits = [
                    {
                        "id": p.id,
                        "name": f"{p.first_name} {p.last_name}",
                        "mrn": p.mrn,
                        "gender": p.gender,
                        "subtitle": f"{p.mrn} • {p.gender} • Blood {p.blood_group or '-'}",
                    }
                    for p in rows
                ]
            if not self.patient_hits:
                self.error = "No matching patients found."
        except Exception as e:
            logging.exception(f"reports search: {e}")
            self.error = "Failed to run search."
        finally:
            self.loading = False

    @rx.event
    def select_patient(self, patient_id: int):
        self.selected_patient_id = patient_id
        return ReportsState.load_patient_report

    @rx.event
    def load_patient_report(self):
        if not self.selected_patient_id:
            return
        self.loading = True
        try:
            with SessionLocal() as db:
                p = db.get(Patient, self.selected_patient_id)
                if p is None:
                    self.loading = False
                    return
                from datetime import date as _d

                today = _d.today()
                age = (
                    today.year
                    - p.date_of_birth.year
                    - (
                        (today.month, today.day)
                        < (p.date_of_birth.month, p.date_of_birth.day)
                    )
                )
                self.patient_info = {
                    "id": p.id,
                    "name": f"{p.first_name} {p.last_name}",
                    "mrn": p.mrn,
                    "gender": p.gender,
                    "dob": p.date_of_birth.strftime("%Y-%m-%d"),
                    "age": str(age),
                    "blood": p.blood_group or "-",
                    "phone": p.phone or "-",
                    "email": p.email or "-",
                    "address": p.address or "-",
                    "emergency": p.emergency_contact or "-",
                }
                cons = (
                    db.query(Consultation, User)
                    .join(User, Consultation.doctor_id == User.id)
                    .filter(Consultation.patient_id == p.id)
                    .order_by(Consultation.visit_date.desc())
                    .all()
                )
                self.consultations = [
                    {
                        "date": c.visit_date.strftime("%Y-%m-%d"),
                        "title": c.diagnosis or "-",
                        "detail": c.chief_complaint or "-",
                        "extra": u.full_name,
                    }
                    for c, u in cons
                ]
                pres = (
                    db.query(Prescription, User)
                    .join(User, Prescription.doctor_id == User.id)
                    .filter(Prescription.patient_id == p.id)
                    .order_by(Prescription.issued_on.desc())
                    .all()
                )
                self.prescriptions = [
                    {
                        "date": pr.issued_on.strftime("%Y-%m-%d"),
                        "title": pr.medication,
                        "detail": f"{pr.dosage} • {pr.frequency} • {pr.duration}",
                        "extra": u.full_name,
                    }
                    for pr, u in pres
                ]
                labs = (
                    db.query(LaboratoryReport)
                    .filter(LaboratoryReport.patient_id == p.id)
                    .order_by(LaboratoryReport.performed_on.desc())
                    .all()
                )
                self.labs = [
                    {
                        "date": l.performed_on.strftime("%Y-%m-%d"),
                        "title": l.test_name,
                        "detail": f"Result: {l.result or '-'}",
                        "extra": l.status,
                    }
                    for l in labs
                ]
        except Exception as e:
            logging.exception(f"reports load_patient_report: {e}")
        finally:
            self.loading = False

    def _create_patient_report_pdf(self) -> str:
        filename = generate_patient_report_pdf(
            {
                "patient": self.patient_info,
                "consultations": self.consultations,
                "prescriptions": self.prescriptions,
                "labs": self.labs,
            }
        )
        with SessionLocal() as db:
            db.add(ReportLog(kind="Patient Summary", generated_by="admin"))
            db.commit()
        self.generated_pdf = filename
        return filename

    @rx.event
    def generate_medical_report(self):
        if not self.selected_patient_id:
            return rx.toast.error("Select a patient first.")
        try:
            filename = self._create_patient_report_pdf()
            self.success_message = "Medical report generated successfully."
            yield rx.toast.success("Medical report generated.")
            yield rx.download(
                url=f"/_upload/{filename}",
                filename=f"patient_report_{self.patient_info['mrn']}.pdf",
            )
        except Exception as e:
            logging.exception(f"generate_medical_report: {e}")
            yield rx.toast.error("Failed to generate report.")

    @rx.event
    def download_pdf(self):
        if not self.selected_patient_id:
            return rx.toast.error("Select a patient first.")
        try:
            filename = self._create_patient_report_pdf()
            return rx.download(
                url=f"/_upload/{filename}",
                filename=f"patient_report_{self.patient_info['mrn']}.pdf",
            )
        except Exception as e:
            logging.exception(f"download_pdf: {e}")
            return rx.toast.error("Failed to generate report.")

    @rx.event
    def print_page(self):
        return rx.call_script("window.print()")
