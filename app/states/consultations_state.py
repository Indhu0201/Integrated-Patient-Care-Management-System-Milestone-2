import logging
from datetime import date, datetime
from typing import TypedDict

import reflex as rx
from sqlalchemy import func

from app.database import (
    Consultation,
    DiagnosisHistory,
    MedicalHistory,
    Patient,
    Prescription,
    SessionLocal,
    User,
)
from app.states.common import (
    DoctorOption,
    PatientOption,
    load_doctor_options,
    load_patient_options,
)


class ConsultationRow(TypedDict):
    id: int
    patient_id: int
    doctor_id: int
    patient: str
    doctor: str
    date: str
    symptoms: str
    diagnosis: str
    treatment: str
    status: str


class ConsultationsState(rx.State):
    loading: bool = False
    patients: list[PatientOption] = []
    doctors: list[DoctorOption] = []
    rows: list[ConsultationRow] = []

    search_query: str = ""
    page: int = 0
    page_size: int = 10
    sort_desc: bool = True

    # Form
    form_open: bool = False
    editing_id: int = 0
    form_patient_id: int = 0
    form_doctor_id: int = 0
    form_date: str = ""
    form_symptoms: str = ""
    form_diagnosis: str = ""
    form_treatment: str = ""
    form_error: str = ""
    success_message: str = ""

    # View / Delete
    view_open: bool = False
    view_row: ConsultationRow = {
        "id": 0,
        "patient_id": 0,
        "doctor_id": 0,
        "patient": "",
        "doctor": "",
        "date": "",
        "symptoms": "",
        "diagnosis": "",
        "treatment": "",
        "status": "",
    }
    delete_id: int = 0
    delete_open: bool = False

    @rx.var
    def total_count(self) -> int:
        return len(self._filtered())

    @rx.var
    def total_pages(self) -> int:
        n = self.total_count
        return max(1, (n + self.page_size - 1) // self.page_size)

    @rx.var
    def page_rows(self) -> list[ConsultationRow]:
        data = self._filtered()
        start = self.page * self.page_size
        return data[start : start + self.page_size]

    def _filtered(self) -> list[ConsultationRow]:
        q = self.search_query.strip().lower()
        data = self.rows
        if q:
            data = [
                r
                for r in data
                if q in r["patient"].lower()
                or q in r["doctor"].lower()
                or q in r["diagnosis"].lower()
                or q in r["symptoms"].lower()
            ]
        data = sorted(data, key=lambda r: r["date"], reverse=self.sort_desc)
        return data

    @rx.event
    def load_page(self):
        self.patients = load_patient_options()
        self.doctors = load_doctor_options()
        return ConsultationsState.load_rows

    @rx.event
    def load_rows(self):
        self.loading = True
        try:
            with SessionLocal() as db:
                rows = (
                    db.query(Consultation, Patient, User)
                    .join(Patient, Consultation.patient_id == Patient.id)
                    .join(User, Consultation.doctor_id == User.id)
                    .order_by(Consultation.visit_date.desc())
                    .limit(500)
                    .all()
                )
                self.rows = [
                    {
                        "id": c.id,
                        "patient_id": p.id,
                        "doctor_id": u.id,
                        "patient": f"{p.first_name} {p.last_name}",
                        "doctor": u.full_name,
                        "date": c.visit_date.strftime("%Y-%m-%d"),
                        "symptoms": c.chief_complaint or "",
                        "diagnosis": c.diagnosis or "",
                        "treatment": c.notes or "",
                        "status": c.status or "Completed",
                    }
                    for c, p, u in rows
                ]
        except Exception as e:
            logging.exception(f"load_rows: {e}")
        finally:
            self.loading = False

    @rx.event
    def set_search_query(self, value: str):
        self.search_query = value
        self.page = 0

    @rx.event
    def toggle_sort(self):
        self.sort_desc = not self.sort_desc

    @rx.event
    def next_page(self):
        if self.page + 1 < self.total_pages:
            self.page += 1

    @rx.event
    def prev_page(self):
        if self.page > 0:
            self.page -= 1

    # ---- Form ----
    def _reset_form(self):
        self.editing_id = 0
        self.form_patient_id = self.patients[0]["id"] if self.patients else 0
        self.form_doctor_id = self.doctors[0]["id"] if self.doctors else 0
        self.form_date = date.today().strftime("%Y-%m-%d")
        self.form_symptoms = ""
        self.form_diagnosis = ""
        self.form_treatment = ""
        self.form_error = ""

    @rx.event
    def open_new(self):
        self._reset_form()
        self.success_message = ""
        self.form_open = True

    @rx.event
    def close_form(self):
        self.form_open = False

    @rx.event
    def reset_form(self):
        self._reset_form()

    @rx.event
    def open_edit(self, row_id: int):
        row = next((r for r in self.rows if r["id"] == row_id), None)
        if row is None:
            return
        self.editing_id = row_id
        self.form_patient_id = row["patient_id"]
        self.form_doctor_id = row["doctor_id"]
        self.form_date = row["date"]
        self.form_symptoms = row["symptoms"]
        self.form_diagnosis = row["diagnosis"]
        self.form_treatment = row["treatment"]
        self.form_error = ""
        self.success_message = ""
        self.form_open = True

    @rx.event
    def set_form_patient(self, value: str):
        try:
            self.form_patient_id = int(value)
        except ValueError:
            pass

    @rx.event
    def set_form_doctor(self, value: str):
        try:
            self.form_doctor_id = int(value)
        except ValueError:
            pass

    @rx.event
    def set_form_date(self, value: str):
        self.form_date = value

    @rx.event
    def set_form_symptoms(self, value: str):
        self.form_symptoms = value

    @rx.event
    def set_form_diagnosis(self, value: str):
        self.form_diagnosis = value

    @rx.event
    def set_form_treatment(self, value: str):
        self.form_treatment = value

    @rx.event
    def save_consultation(self):
        if not self.form_patient_id:
            self.form_error = "Please select a patient."
            return
        if not self.form_doctor_id:
            self.form_error = "Please select a doctor."
            return
        if not self.form_date:
            self.form_error = "Date is required."
            return
        try:
            visit_dt = datetime.strptime(self.form_date, "%Y-%m-%d")
        except ValueError:
            self.form_error = "Invalid date format (YYYY-MM-DD)."
            return
        if not self.form_symptoms.strip():
            self.form_error = "Symptoms are required."
            return
        if not self.form_diagnosis.strip():
            self.form_error = "Diagnosis is required."
            return

        try:
            with SessionLocal() as db:
                # Validate patient and doctor exist
                p = db.get(Patient, self.form_patient_id)
                u = db.get(User, self.form_doctor_id)
                if p is None or u is None:
                    self.form_error = "Selected patient or doctor not found."
                    return
                if self.editing_id:
                    c = db.get(Consultation, self.editing_id)
                    if c is None:
                        self.form_error = "Consultation not found."
                        return
                else:
                    c = Consultation()
                    db.add(c)
                c.patient_id = self.form_patient_id
                c.doctor_id = self.form_doctor_id
                c.visit_date = visit_dt
                c.chief_complaint = self.form_symptoms.strip()
                c.diagnosis = self.form_diagnosis.strip()
                c.notes = self.form_treatment.strip()
                c.status = "Completed"
                db.flush()

                # Update linked medical history / diagnosis history for new records
                if not self.editing_id:
                    db.add(
                        DiagnosisHistory(
                            patient_id=c.patient_id,
                            diagnosis=c.diagnosis,
                            diagnosed_on=visit_dt.date(),
                            doctor_id=c.doctor_id,
                        )
                    )
                    db.add(
                        MedicalHistory(
                            patient_id=c.patient_id,
                            condition=c.diagnosis,
                            onset_date=visit_dt.date(),
                            notes=c.notes,
                        )
                    )
                db.commit()
            self.form_open = False
            self.success_message = "Consultation saved successfully."
            yield rx.toast.success("Consultation saved.")
            yield ConsultationsState.load_rows
        except Exception as e:
            logging.exception(f"save_consultation: {e}")
            self.form_error = "Failed to save consultation."

    @rx.event
    def open_view(self, row_id: int):
        row = next((r for r in self.rows if r["id"] == row_id), None)
        if row is None:
            return
        self.view_row = row
        self.view_open = True

    @rx.event
    def close_view(self):
        self.view_open = False

    @rx.event
    def confirm_delete(self, row_id: int):
        self.delete_id = row_id
        self.delete_open = True

    @rx.event
    def cancel_delete(self):
        self.delete_open = False
        self.delete_id = 0

    @rx.event
    def delete_consultation(self):
        if not self.delete_id:
            return
        try:
            with SessionLocal() as db:
                c = db.get(Consultation, self.delete_id)
                if c is not None:
                    # Remove any prescriptions linking to this consultation.
                    db.query(Prescription).filter(
                        Prescription.consultation_id == c.id
                    ).update({Prescription.consultation_id: None})
                    db.delete(c)
                    db.commit()
            self.delete_open = False
            self.delete_id = 0
            yield rx.toast.success("Consultation deleted.")
            yield ConsultationsState.load_rows
        except Exception as e:
            logging.exception(f"delete_consultation: {e}")
            yield rx.toast.error("Failed to delete consultation.")

    @rx.event
    def print_page(self):
        return rx.call_script("window.print()")
