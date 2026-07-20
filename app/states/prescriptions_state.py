import logging
from datetime import date, datetime
from typing import TypedDict

import reflex as rx

from app.database import Patient, Prescription, SessionLocal, User
from app.states.common import (
    DoctorOption,
    PatientOption,
    load_doctor_options,
    load_patient_options,
)
from app.utils.pdf import generate_prescription_pdf


class PrescriptionRow(TypedDict):
    id: int
    patient_id: int
    doctor_id: int
    patient: str
    doctor: str
    medication: str
    dosage: str
    frequency: str
    duration: str
    instructions: str
    date: str
    status: str


FREQUENCIES = [
    "Once daily",
    "Twice daily",
    "Three times daily",
    "Every 8 hours",
    "As needed",
]


class PrescriptionsState(rx.State):
    loading: bool = False
    patients: list[PatientOption] = []
    doctors: list[DoctorOption] = []
    frequencies: list[str] = FREQUENCIES
    rows: list[PrescriptionRow] = []

    search_query: str = ""
    page: int = 0
    page_size: int = 10
    sort_desc: bool = True

    # Form
    form_open: bool = False
    editing_id: int = 0
    form_patient_id: int = 0
    form_doctor_id: int = 0
    form_medication: str = ""
    form_dosage: str = ""
    form_frequency: str = "Once daily"
    form_duration: str = ""
    form_instructions: str = ""
    form_date: str = ""
    form_error: str = ""
    success_message: str = ""

    # View / delete
    view_open: bool = False
    view_row: PrescriptionRow = {
        "id": 0,
        "patient_id": 0,
        "doctor_id": 0,
        "patient": "",
        "doctor": "",
        "medication": "",
        "dosage": "",
        "frequency": "",
        "duration": "",
        "instructions": "",
        "date": "",
        "status": "",
    }
    delete_id: int = 0
    delete_open: bool = False

    # PDF
    generated_pdf: str = ""

    @rx.var
    def total_count(self) -> int:
        return len(self._filtered())

    @rx.var
    def total_pages(self) -> int:
        n = self.total_count
        return max(1, (n + self.page_size - 1) // self.page_size)

    @rx.var
    def page_rows(self) -> list[PrescriptionRow]:
        data = self._filtered()
        start = self.page * self.page_size
        return data[start : start + self.page_size]

    def _filtered(self) -> list[PrescriptionRow]:
        q = self.search_query.strip().lower()
        data = self.rows
        if q:
            data = [
                r
                for r in data
                if q in r["patient"].lower()
                or q in r["doctor"].lower()
                or q in r["medication"].lower()
            ]
        data = sorted(data, key=lambda r: r["date"], reverse=self.sort_desc)
        return data

    @rx.event
    def load_page(self):
        self.patients = load_patient_options()
        self.doctors = load_doctor_options()
        return PrescriptionsState.load_rows

    @rx.event
    def load_rows(self):
        self.loading = True
        try:
            with SessionLocal() as db:
                rows = (
                    db.query(Prescription, Patient, User)
                    .join(Patient, Prescription.patient_id == Patient.id)
                    .join(User, Prescription.doctor_id == User.id)
                    .order_by(Prescription.issued_on.desc())
                    .limit(500)
                    .all()
                )
                self.rows = [
                    {
                        "id": pr.id,
                        "patient_id": p.id,
                        "doctor_id": u.id,
                        "patient": f"{p.first_name} {p.last_name}",
                        "doctor": u.full_name,
                        "medication": pr.medication,
                        "dosage": pr.dosage or "",
                        "frequency": pr.frequency or "",
                        "duration": pr.duration or "",
                        "instructions": pr.instructions or "",
                        "date": pr.issued_on.strftime("%Y-%m-%d"),
                        "status": pr.status or "Active",
                    }
                    for pr, p, u in rows
                ]
        except Exception as e:
            logging.exception(f"prescriptions load_rows: {e}")
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

    def _reset_form(self):
        self.editing_id = 0
        self.form_patient_id = self.patients[0]["id"] if self.patients else 0
        self.form_doctor_id = self.doctors[0]["id"] if self.doctors else 0
        self.form_medication = ""
        self.form_dosage = ""
        self.form_frequency = "Once daily"
        self.form_duration = ""
        self.form_instructions = ""
        self.form_date = date.today().strftime("%Y-%m-%d")
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
    def open_edit(self, row_id: int):
        row = next((r for r in self.rows if r["id"] == row_id), None)
        if row is None:
            return
        self.editing_id = row_id
        self.form_patient_id = row["patient_id"]
        self.form_doctor_id = row["doctor_id"]
        self.form_medication = row["medication"]
        self.form_dosage = row["dosage"]
        self.form_frequency = row["frequency"] or "Once daily"
        self.form_duration = row["duration"]
        self.form_instructions = row["instructions"]
        self.form_date = row["date"]
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
    def set_form_medication(self, value: str):
        self.form_medication = value

    @rx.event
    def set_form_dosage(self, value: str):
        self.form_dosage = value

    @rx.event
    def set_form_frequency(self, value: str):
        self.form_frequency = value

    @rx.event
    def set_form_duration(self, value: str):
        self.form_duration = value

    @rx.event
    def set_form_instructions(self, value: str):
        self.form_instructions = value

    @rx.event
    def set_form_date(self, value: str):
        self.form_date = value

    def _validate(self) -> str:
        if not self.form_patient_id:
            return "Please select a patient."
        if not self.form_doctor_id:
            return "Please select a doctor."
        if not self.form_medication.strip():
            return "Medicine is required."
        if not self.form_dosage.strip():
            return "Dosage is required."
        if not self.form_frequency.strip():
            return "Frequency is required."
        if not self.form_duration.strip():
            return "Duration is required."
        if not self.form_date:
            return "Date is required."
        try:
            datetime.strptime(self.form_date, "%Y-%m-%d")
        except ValueError:
            return "Invalid date format (YYYY-MM-DD)."
        return ""

    @rx.event
    def save_prescription(self):
        err = self._validate()
        if err:
            self.form_error = err
            return
        try:
            issued = datetime.strptime(self.form_date, "%Y-%m-%d")
            with SessionLocal() as db:
                if db.get(Patient, self.form_patient_id) is None:
                    self.form_error = "Selected patient not found."
                    return
                if db.get(User, self.form_doctor_id) is None:
                    self.form_error = "Selected doctor not found."
                    return
                if self.editing_id:
                    pr = db.get(Prescription, self.editing_id)
                    if pr is None:
                        self.form_error = "Prescription not found."
                        return
                else:
                    pr = Prescription()
                    db.add(pr)
                pr.patient_id = self.form_patient_id
                pr.doctor_id = self.form_doctor_id
                pr.medication = self.form_medication.strip()
                pr.dosage = self.form_dosage.strip()
                pr.frequency = self.form_frequency.strip()
                pr.duration = self.form_duration.strip()
                pr.instructions = self.form_instructions.strip()
                pr.issued_on = issued
                pr.status = "Active"
                db.commit()
            self.form_open = False
            self.success_message = "Prescription saved successfully."
            yield rx.toast.success("Prescription saved.")
            yield PrescriptionsState.load_rows
        except Exception as e:
            logging.exception(f"save_prescription: {e}")
            self.form_error = "Failed to save prescription."

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
    def delete_prescription(self):
        if not self.delete_id:
            return
        try:
            with SessionLocal() as db:
                pr = db.get(Prescription, self.delete_id)
                if pr is not None:
                    db.delete(pr)
                    db.commit()
            self.delete_open = False
            self.delete_id = 0
            yield rx.toast.success("Prescription deleted.")
            yield PrescriptionsState.load_rows
        except Exception as e:
            logging.exception(f"delete_prescription: {e}")
            yield rx.toast.error("Failed to delete prescription.")

    @rx.event
    def download_pdf(self, row_id: int):
        row = next((r for r in self.rows if r["id"] == row_id), None)
        if row is None:
            return
        try:
            filename = generate_prescription_pdf(
                {
                    "patient": row["patient"],
                    "doctor": row["doctor"],
                    "date": row["date"],
                    "medication": row["medication"],
                    "dosage": row["dosage"],
                    "frequency": row["frequency"],
                    "duration": row["duration"],
                    "instructions": row["instructions"],
                }
            )
            self.generated_pdf = filename
            return rx.download(
                url=f"/_upload/{filename}",
                filename=f"prescription_{row['id']}.pdf",
            )
        except Exception as e:
            logging.exception(f"download_pdf: {e}")
            return rx.toast.error("Failed to generate PDF.")

    @rx.event
    def print_page(self):
        return rx.call_script("window.print()")
