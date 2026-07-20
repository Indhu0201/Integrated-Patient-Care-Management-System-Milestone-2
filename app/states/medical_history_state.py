import logging
from datetime import date, datetime
from typing import TypedDict

import reflex as rx

from app.database import (
    Allergy,
    Consultation,
    DiagnosisHistory,
    LaboratoryReport,
    MedicalHistory,
    Medication,
    Patient,
    Prescription,
    ReportLog,
    SessionLocal,
    User,
)
from app.states.common import PatientOption, load_patient_options
from app.utils.pdf import generate_medical_history_pdf


class Row(TypedDict):
    date: str
    title: str
    detail: str
    extra: str


class PatientInfo(TypedDict):
    id: int
    name: str
    mrn: str
    gender: str
    dob: str
    age: str
    blood: str
    phone: str
    email: str
    address: str
    emergency: str


EMPTY_PATIENT: PatientInfo = {
    "id": 0,
    "name": "",
    "mrn": "",
    "gender": "",
    "dob": "",
    "age": "",
    "blood": "",
    "phone": "",
    "email": "",
    "address": "",
    "emergency": "",
}


class MedicalHistoryState(rx.State):
    loading: bool = False
    search_query: str = ""
    patients: list[PatientOption] = []
    patient_results: list[PatientOption] = []
    selected_patient_id: int = 0

    patient_info: PatientInfo = EMPTY_PATIENT
    consultations: list[Row] = []
    diagnoses: list[Row] = []
    prescriptions: list[Row] = []
    labs: list[Row] = []
    allergies: list[Row] = []
    medications: list[Row] = []
    history_entries: list[dict[str, str]] = []

    generated_pdf: str = ""
    success_message: str = ""

    # Update modal
    update_open: bool = False
    update_edit_id: int = 0
    update_condition: str = ""
    update_onset: str = ""
    update_notes: str = ""
    update_error: str = ""

    @rx.var
    def has_patient(self) -> bool:
        return self.selected_patient_id != 0

    @rx.event
    def load_page(self):
        self.patients = load_patient_options()
        self.patient_results = self.patients[:20]

    @rx.event
    def set_search_query(self, value: str):
        self.search_query = value
        q = value.strip().lower()
        if not q:
            self.patient_results = self.patients[:20]
        else:
            self.patient_results = [
                p
                for p in self.patients
                if q in p["label"].lower()
                or q in str(p["id"])
                or q in p["mrn"].lower()
            ][:20]

    @rx.event
    def select_patient(self, patient_id: int):
        self.selected_patient_id = patient_id
        return MedicalHistoryState.load_history

    @rx.event
    def load_history(self):
        if not self.selected_patient_id:
            return
        self.loading = True
        try:
            with SessionLocal() as db:
                p = db.get(Patient, self.selected_patient_id)
                if p is None:
                    self.loading = False
                    return
                today = date.today()
                age_years = (
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
                    "age": str(age_years),
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

                dx = (
                    db.query(DiagnosisHistory)
                    .filter(DiagnosisHistory.patient_id == p.id)
                    .order_by(DiagnosisHistory.diagnosed_on.desc())
                    .all()
                )
                self.diagnoses = [
                    {
                        "date": d.diagnosed_on.strftime("%Y-%m-%d")
                        if d.diagnosed_on
                        else "",
                        "title": d.diagnosis,
                        "detail": "",
                        "extra": "",
                    }
                    for d in dx
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

                al = db.query(Allergy).filter(Allergy.patient_id == p.id).all()
                self.allergies = [
                    {
                        "date": "",
                        "title": a.allergen,
                        "detail": a.reaction or "-",
                        "extra": a.severity,
                    }
                    for a in al
                ]

                meds = (
                    db.query(Medication)
                    .filter(Medication.patient_id == p.id)
                    .order_by(Medication.started_on.desc())
                    .all()
                )
                self.medications = [
                    {
                        "date": m.started_on.strftime("%Y-%m-%d")
                        if m.started_on
                        else "",
                        "title": m.name,
                        "detail": m.dosage or "-",
                        "extra": "Active" if m.active else "Inactive",
                    }
                    for m in meds
                ]

                hist = (
                    db.query(MedicalHistory)
                    .filter(MedicalHistory.patient_id == p.id)
                    .order_by(MedicalHistory.onset_date.desc())
                    .all()
                )
                self.history_entries = [
                    {
                        "id": str(h.id),
                        "condition": h.condition,
                        "onset": h.onset_date.strftime("%Y-%m-%d")
                        if h.onset_date
                        else "",
                        "notes": h.notes or "",
                    }
                    for h in hist
                ]
        except Exception as e:
            logging.exception(f"medical_history load: {e}")
        finally:
            self.loading = False

    # ---- Update (Medical History entries) ----
    @rx.event
    def open_update_new(self):
        if not self.selected_patient_id:
            return
        self.update_edit_id = 0
        self.update_condition = ""
        self.update_onset = date.today().strftime("%Y-%m-%d")
        self.update_notes = ""
        self.update_error = ""
        self.update_open = True

    @rx.event
    def open_update_edit(self, entry_id: str):
        entry = next(
            (h for h in self.history_entries if h["id"] == entry_id), None
        )
        if entry is None:
            return
        self.update_edit_id = int(entry_id)
        self.update_condition = entry["condition"]
        self.update_onset = entry["onset"] or date.today().strftime("%Y-%m-%d")
        self.update_notes = entry["notes"]
        self.update_error = ""
        self.update_open = True

    @rx.event
    def close_update(self):
        self.update_open = False

    @rx.event
    def set_update_condition(self, value: str):
        self.update_condition = value

    @rx.event
    def set_update_onset(self, value: str):
        self.update_onset = value

    @rx.event
    def set_update_notes(self, value: str):
        self.update_notes = value

    @rx.event
    def save_update(self):
        if not self.update_condition.strip():
            self.update_error = "Condition is required."
            return
        try:
            onset = datetime.strptime(self.update_onset, "%Y-%m-%d").date()
        except ValueError:
            self.update_error = "Invalid onset date (YYYY-MM-DD)."
            return
        if onset > date.today():
            self.update_error = "Onset date cannot be in the future."
            return
        try:
            with SessionLocal() as db:
                if self.update_edit_id:
                    h = db.get(MedicalHistory, self.update_edit_id)
                    if h is None:
                        self.update_error = "Entry not found."
                        return
                else:
                    h = MedicalHistory(patient_id=self.selected_patient_id)
                    db.add(h)
                h.condition = self.update_condition.strip()
                h.onset_date = onset
                h.notes = self.update_notes.strip()
                db.commit()
            self.update_open = False
            yield rx.toast.success("Medical history updated.")
            yield MedicalHistoryState.load_history
        except Exception as e:
            logging.exception(f"save_update medical history: {e}")
            self.update_error = "Failed to save entry."

    @rx.event
    def delete_history_entry(self, entry_id: str):
        try:
            with SessionLocal() as db:
                h = db.get(MedicalHistory, int(entry_id))
                if h is not None:
                    db.delete(h)
                    db.commit()
            yield rx.toast.success("Entry deleted.")
            yield MedicalHistoryState.load_history
        except Exception as e:
            logging.exception(f"delete_history_entry: {e}")
            yield rx.toast.error("Failed to delete entry.")

    # ---- Actions ----
    @rx.event
    def download_pdf(self):
        if not self.selected_patient_id:
            return rx.toast.error("Select a patient first.")
        try:
            filename = generate_medical_history_pdf(
                {
                    "patient": self.patient_info,
                    "consultations": self.consultations,
                    "diagnoses": self.diagnoses,
                    "prescriptions": self.prescriptions,
                    "labs": self.labs,
                    "allergies": self.allergies,
                    "medications": self.medications,
                    "history": self.history_entries,
                }
            )
            with SessionLocal() as db:
                db.add(ReportLog(kind="Medical History", generated_by="admin"))
                db.commit()
            self.generated_pdf = filename
            return rx.download(
                url=f"/_upload/{filename}",
                filename=f"medical_history_{self.patient_info['mrn']}.pdf",
            )
        except Exception as e:
            logging.exception(f"medical_history download_pdf: {e}")
            return rx.toast.error("Failed to generate PDF.")

    @rx.event
    def print_page(self):
        return rx.call_script("window.print()")
