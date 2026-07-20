import logging
from datetime import date, datetime
from typing import TypedDict

import reflex as rx

from app.database import (
    Allergy,
    DiagnosisHistory,
    Document,
    LaboratoryReport,
    Medication,
    MedicalSummary,
    Patient,
    SessionLocal,
    User,
)
from app.states.common import PatientOption, load_patient_options
from app.utils.pdf import generate_ehr_record_pdf


class DiagnosisRow(TypedDict):
    id: int
    date: str
    diagnosis: str
    notes: str


class AllergyRow(TypedDict):
    id: int
    allergen: str
    severity: str
    reaction: str


class MedicationRow(TypedDict):
    id: int
    name: str
    dosage: str
    frequency: str
    started_on: str


class LabRow(TypedDict):
    id: int
    test: str
    date: str
    result: str
    status: str


class DocumentRow(TypedDict):
    id: int
    title: str
    doc_type: str
    uploaded_on: str


class SummaryDict(TypedDict):
    height_cm: str
    weight_kg: str
    bmi: str
    smoking: str
    alcohol: str
    chronic_diseases: str
    remarks: str


class EHRState(rx.State):
    loading: bool = False
    patient_options: list[PatientOption] = []
    selected_patient_id: int = 0
    patient_search: str = ""
    active_tab: str = "summary"

    # Patient header info
    patient_name: str = ""
    patient_mrn: str = ""
    patient_gender: str = ""
    patient_dob: str = ""
    patient_blood: str = ""
    patient_phone: str = ""
    patient_email: str = ""
    patient_address: str = ""
    patient_emergency: str = ""

    summary: SummaryDict = {
        "height_cm": "",
        "weight_kg": "",
        "bmi": "",
        "smoking": "No",
        "alcohol": "No",
        "chronic_diseases": "",
        "remarks": "",
    }
    edit_summary_open: bool = False
    summary_error: str = ""

    diagnoses: list[DiagnosisRow] = []
    allergies: list[AllergyRow] = []
    medications: list[MedicationRow] = []
    labs: list[LabRow] = []
    documents: list[DocumentRow] = []
    generated_pdf: str = ""

    # Allergy modal
    allergy_modal_open: bool = False
    allergy_edit_id: int = 0
    allergy_form: dict[str, str] = {
        "allergen": "",
        "severity": "Mild",
        "reaction": "",
    }
    allergy_error: str = ""

    @rx.var
    def filtered_patient_options(self) -> list[PatientOption]:
        q = self.patient_search.strip().lower()
        if not q:
            return self.patient_options[:50]
        return [p for p in self.patient_options if q in p["label"].lower()][:50]

    @rx.event
    def load_page(self):
        self.patient_options = load_patient_options()
        if self.patient_options and self.selected_patient_id == 0:
            self.selected_patient_id = self.patient_options[0]["id"]
            return EHRState.load_patient

    @rx.event
    def set_patient_search(self, value: str):
        self.patient_search = value

    @rx.event
    def select_patient(self, patient_id: int):
        self.selected_patient_id = patient_id
        return EHRState.load_patient

    @rx.event
    def set_active_tab(self, tab: str):
        self.active_tab = tab

    @rx.event
    def load_patient(self):
        if not self.selected_patient_id:
            return
        self.loading = True
        try:
            with SessionLocal() as db:
                p = db.get(Patient, self.selected_patient_id)
                if p is None:
                    self.loading = False
                    return
                self.patient_name = f"{p.first_name} {p.last_name}"
                self.patient_mrn = p.mrn
                self.patient_gender = p.gender
                self.patient_dob = p.date_of_birth.strftime("%Y-%m-%d")
                self.patient_blood = p.blood_group or "-"
                self.patient_phone = p.phone or "-"
                self.patient_email = p.email or "-"
                self.patient_address = p.address or "-"
                self.patient_emergency = p.emergency_contact or "-"

                s = (
                    db.query(MedicalSummary)
                    .filter(MedicalSummary.patient_id == p.id)
                    .first()
                )
                if s is None:
                    self.summary = {
                        "height_cm": "",
                        "weight_kg": "",
                        "bmi": "",
                        "smoking": "No",
                        "alcohol": "No",
                        "chronic_diseases": "",
                        "remarks": "",
                    }
                else:
                    self.summary = {
                        "height_cm": s.height_cm or "",
                        "weight_kg": s.weight_kg or "",
                        "bmi": s.bmi or "",
                        "smoking": s.smoking or "No",
                        "alcohol": s.alcohol or "No",
                        "chronic_diseases": s.chronic_diseases or "",
                        "remarks": s.remarks or "",
                    }

                dx = (
                    db.query(DiagnosisHistory)
                    .filter(DiagnosisHistory.patient_id == p.id)
                    .order_by(DiagnosisHistory.diagnosed_on.desc())
                    .all()
                )
                self.diagnoses = [
                    {
                        "id": d.id,
                        "date": d.diagnosed_on.strftime("%Y-%m-%d")
                        if d.diagnosed_on
                        else "",
                        "diagnosis": d.diagnosis,
                        "notes": "",
                    }
                    for d in dx
                ]

                al = db.query(Allergy).filter(Allergy.patient_id == p.id).all()
                self.allergies = [
                    {
                        "id": a.id,
                        "allergen": a.allergen,
                        "severity": a.severity,
                        "reaction": a.reaction,
                    }
                    for a in al
                ]

                meds = (
                    db.query(Medication)
                    .filter(Medication.patient_id == p.id, Medication.active)
                    .order_by(Medication.started_on.desc())
                    .all()
                )
                self.medications = [
                    {
                        "id": m.id,
                        "name": m.name,
                        "dosage": m.dosage,
                        "frequency": "Once daily",
                        "started_on": m.started_on.strftime("%Y-%m-%d")
                        if m.started_on
                        else "",
                    }
                    for m in meds
                ]

                lb = (
                    db.query(LaboratoryReport)
                    .filter(LaboratoryReport.patient_id == p.id)
                    .order_by(LaboratoryReport.performed_on.desc())
                    .all()
                )
                self.labs = [
                    {
                        "id": l.id,
                        "test": l.test_name,
                        "date": l.performed_on.strftime("%Y-%m-%d"),
                        "result": l.result,
                        "status": l.status,
                    }
                    for l in lb
                ]

                docs = (
                    db.query(Document)
                    .filter(Document.patient_id == p.id)
                    .order_by(Document.uploaded_on.desc())
                    .all()
                )
                self.documents = [
                    {
                        "id": d.id,
                        "title": d.title,
                        "doc_type": d.doc_type,
                        "uploaded_on": d.uploaded_on.strftime("%Y-%m-%d"),
                    }
                    for d in docs
                ]
        except Exception as e:
            logging.exception(f"EHR load_patient: {e}")
        finally:
            self.loading = False

    # ---- Medical Summary ----
    @rx.event
    def open_edit_summary(self):
        self.summary_error = ""
        self.edit_summary_open = True

    @rx.event
    def close_edit_summary(self):
        self.edit_summary_open = False

    @rx.event
    def save_summary(self, form_data: dict):
        height = (form_data.get("height_cm") or "").strip()
        weight = (form_data.get("weight_kg") or "").strip()
        if not height or not weight:
            self.summary_error = "Height and Weight are required."
            return
        try:
            h = float(height)
            w = float(weight)
            if h <= 0 or w <= 0:
                self.summary_error = "Height/Weight must be positive numbers."
                return
            bmi = round(w / ((h / 100) ** 2), 1)
        except ValueError:
            self.summary_error = "Height/Weight must be numeric."
            return

        try:
            with SessionLocal() as db:
                s = (
                    db.query(MedicalSummary)
                    .filter(
                        MedicalSummary.patient_id == self.selected_patient_id
                    )
                    .first()
                )
                if s is None:
                    s = MedicalSummary(patient_id=self.selected_patient_id)
                    db.add(s)
                s.height_cm = height
                s.weight_kg = weight
                s.bmi = str(bmi)
                s.smoking = form_data.get("smoking") or "No"
                s.alcohol = form_data.get("alcohol") or "No"
                s.chronic_diseases = form_data.get("chronic_diseases") or ""
                s.remarks = form_data.get("remarks") or ""
                s.updated_on = datetime.utcnow()
                db.commit()
            self.edit_summary_open = False
            yield rx.toast.success("Medical summary saved.")
            yield EHRState.load_patient
        except Exception as e:
            logging.exception(f"save_summary: {e}")
            self.summary_error = "Failed to save summary."

    # ---- Allergies ----
    @rx.event
    def open_add_allergy(self):
        self.allergy_edit_id = 0
        self.allergy_form = {"allergen": "", "severity": "Mild", "reaction": ""}
        self.allergy_error = ""
        self.allergy_modal_open = True

    @rx.event
    def open_edit_allergy(self, allergy_id: int):
        row = next((a for a in self.allergies if a["id"] == allergy_id), None)
        if row is None:
            return
        self.allergy_edit_id = allergy_id
        self.allergy_form = {
            "allergen": row["allergen"],
            "severity": row["severity"],
            "reaction": row["reaction"],
        }
        self.allergy_error = ""
        self.allergy_modal_open = True

    @rx.event
    def close_allergy_modal(self):
        self.allergy_modal_open = False

    @rx.event
    def save_allergy(self, form_data: dict):
        allergen = (form_data.get("allergen") or "").strip()
        severity = (form_data.get("severity") or "Mild").strip()
        reaction = (form_data.get("reaction") or "").strip()
        if not allergen:
            self.allergy_error = "Allergen is required."
            return
        try:
            with SessionLocal() as db:
                if self.allergy_edit_id:
                    a = db.get(Allergy, self.allergy_edit_id)
                    if a is None:
                        self.allergy_error = "Allergy not found."
                        return
                else:
                    a = Allergy(patient_id=self.selected_patient_id)
                    db.add(a)
                a.allergen = allergen
                a.severity = severity
                a.reaction = reaction
                db.commit()
            self.allergy_modal_open = False
            yield rx.toast.success("Allergy saved.")
            yield EHRState.load_patient
        except Exception as e:
            logging.exception(f"save_allergy: {e}")
            self.allergy_error = "Failed to save allergy."

    @rx.event
    def delete_allergy(self, allergy_id: int):
        try:
            with SessionLocal() as db:
                a = db.get(Allergy, allergy_id)
                if a is not None:
                    db.delete(a)
                    db.commit()
            yield rx.toast.success("Allergy deleted.")
            yield EHRState.load_patient
        except Exception as e:
            logging.exception(f"delete_allergy: {e}")
            yield rx.toast.error("Failed to delete allergy.")

    @rx.event
    def download_record(self):
        if not self.selected_patient_id:
            return rx.toast.error("Select a patient first.")
        try:
            self.generated_pdf = generate_ehr_record_pdf(
                {
                    "patient": {
                        "name": self.patient_name,
                        "mrn": self.patient_mrn,
                        "gender": self.patient_gender,
                        "dob": self.patient_dob,
                        "age": "",
                        "blood": self.patient_blood,
                        "phone": self.patient_phone,
                        "email": self.patient_email,
                        "address": self.patient_address,
                        "emergency": self.patient_emergency,
                    },
                    "summary": self.summary,
                    "diagnoses": [
                        {
                            "date": row["date"],
                            "title": row["diagnosis"],
                            "detail": row["notes"] or "-",
                            "extra": "",
                        }
                        for row in self.diagnoses
                    ],
                    "allergies": [
                        {
                            "date": "",
                            "title": row["allergen"],
                            "detail": row["reaction"] or "-",
                            "extra": row["severity"],
                        }
                        for row in self.allergies
                    ],
                    "medications": [
                        {
                            "date": row["started_on"],
                            "title": row["name"],
                            "detail": row["dosage"] or "-",
                            "extra": row["frequency"] or "-",
                        }
                        for row in self.medications
                    ],
                    "labs": [
                        {
                            "date": row["date"],
                            "title": row["test"],
                            "detail": f"Result: {row['result'] or '-'}",
                            "extra": row["status"],
                        }
                        for row in self.labs
                    ],
                    "documents": [
                        {
                            "date": row["uploaded_on"],
                            "title": row["title"],
                            "detail": row["doc_type"],
                            "extra": "",
                        }
                        for row in self.documents
                    ],
                }
            )
            return rx.download(
                url=f"/_upload/{self.generated_pdf}",
                filename=f"ehr_record_{self.patient_mrn or self.selected_patient_id}.pdf",
            )
        except Exception as e:
            logging.exception(f"EHR record download failed: {e}")
            return rx.toast.error("Failed to generate EHR record PDF.")

    @rx.event
    def print_record(self):
        return rx.call_script("window.print()")
