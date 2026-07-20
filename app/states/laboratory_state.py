import logging
from datetime import date, datetime
from pathlib import Path
from typing import TypedDict

import reflex as rx

from app.database import (
    Document,
    LaboratoryReport,
    Patient,
    SessionLocal,
    User,
)
from app.states.common import (
    DoctorOption,
    PatientOption,
    load_doctor_options,
    load_patient_options,
)
from app.utils.pdf import generate_lab_report_pdf


class LabRow(TypedDict):
    id: int
    patient_id: int
    doctor_id: int
    patient: str
    doctor: str
    test_type: str
    test_name: str
    result: str
    remarks: str
    status: str
    date: str
    file_name: str


TEST_TYPES = [
    "Blood Test",
    "CBC",
    "Urine Test",
    "MRI",
    "CT Scan",
    "X-Ray",
    "ECG",
]
LAB_STATUS = ["Pending", "In Progress", "Completed"]


class LaboratoryState(rx.State):
    loading: bool = False
    patients: list[PatientOption] = []
    doctors: list[DoctorOption] = []
    test_types: list[str] = TEST_TYPES
    status_options: list[str] = LAB_STATUS
    rows: list[LabRow] = []

    search_query: str = ""
    page: int = 0
    page_size: int = 10
    sort_desc: bool = True

    # Form
    form_open: bool = False
    editing_id: int = 0
    form_patient_id: int = 0
    form_doctor_id: int = 0
    form_test_type: str = "Blood Test"
    form_test_name: str = ""
    form_result: str = ""
    form_remarks: str = ""
    form_status: str = "Completed"
    form_date: str = ""
    form_error: str = ""
    form_upload_file: str = ""
    success_message: str = ""

    # View / delete
    view_open: bool = False
    view_row: LabRow = {
        "id": 0,
        "patient_id": 0,
        "doctor_id": 0,
        "patient": "",
        "doctor": "",
        "test_type": "",
        "test_name": "",
        "result": "",
        "remarks": "",
        "status": "",
        "date": "",
        "file_name": "",
    }
    delete_id: int = 0
    delete_open: bool = False

    generated_pdf: str = ""

    @rx.var
    def total_count(self) -> int:
        return len(self._filtered())

    @rx.var
    def total_pages(self) -> int:
        n = self.total_count
        return max(1, (n + self.page_size - 1) // self.page_size)

    @rx.var
    def page_rows(self) -> list[LabRow]:
        data = self._filtered()
        start = self.page * self.page_size
        return data[start : start + self.page_size]

    def _filtered(self) -> list[LabRow]:
        q = self.search_query.strip().lower()
        data = self.rows
        if q:
            data = [
                r
                for r in data
                if q in r["patient"].lower()
                or q in r["doctor"].lower()
                or q in r["test_name"].lower()
                or q in r["test_type"].lower()
            ]
        data = sorted(data, key=lambda r: r["date"], reverse=self.sort_desc)
        return data

    @rx.event
    def load_page(self):
        self.patients = load_patient_options()
        self.doctors = load_doctor_options()
        return LaboratoryState.load_rows

    @rx.event
    def load_rows(self):
        self.loading = True
        try:
            with SessionLocal() as db:
                rows = (
                    db.query(LaboratoryReport, Patient, User)
                    .join(Patient, LaboratoryReport.patient_id == Patient.id)
                    .join(User, LaboratoryReport.doctor_id == User.id)
                    .order_by(LaboratoryReport.performed_on.desc())
                    .limit(500)
                    .all()
                )
                # Fetch documents linked by title convention
                doc_map: dict[int, str] = {}
                docs = (
                    db.query(Document)
                    .filter(Document.doc_type == "Lab Upload")
                    .all()
                )
                for d in docs:
                    # title format: "lab_<id>__<orig>"
                    if d.title.startswith("lab_"):
                        try:
                            lid = int(
                                d.title.split("__", 1)[0].split("_", 1)[1]
                            )
                            doc_map[lid] = d.file_path
                        except Exception:
                            logging.exception("Unexpected error")
                self.rows = [
                    {
                        "id": l.id,
                        "patient_id": p.id,
                        "doctor_id": u.id,
                        "patient": f"{p.first_name} {p.last_name}",
                        "doctor": u.full_name,
                        "test_type": l.test_type,
                        "test_name": l.test_name,
                        "result": l.result or "",
                        "remarks": l.reference_range or "",
                        "status": l.status or "Completed",
                        "date": l.performed_on.strftime("%Y-%m-%d"),
                        "file_name": doc_map.get(l.id, ""),
                    }
                    for l, p, u in rows
                ]
        except Exception as e:
            logging.exception(f"lab load_rows: {e}")
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
        self.form_test_type = "Blood Test"
        self.form_test_name = ""
        self.form_result = ""
        self.form_remarks = ""
        self.form_status = "Completed"
        self.form_date = date.today().strftime("%Y-%m-%d")
        self.form_error = ""
        self.form_upload_file = ""

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
        self.form_test_type = (
            row["test_type"] if row["test_type"] in TEST_TYPES else "Blood Test"
        )
        self.form_test_name = row["test_name"]
        self.form_result = row["result"]
        self.form_remarks = row["remarks"]
        self.form_status = (
            row["status"] if row["status"] in LAB_STATUS else "Completed"
        )
        self.form_date = row["date"]
        self.form_error = ""
        self.form_upload_file = row["file_name"]
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
    def set_form_test_type(self, value: str):
        self.form_test_type = value

    @rx.event
    def set_form_test_name(self, value: str):
        self.form_test_name = value

    @rx.event
    def set_form_result(self, value: str):
        self.form_result = value

    @rx.event
    def set_form_remarks(self, value: str):
        self.form_remarks = value

    @rx.event
    def set_form_status(self, value: str):
        self.form_status = value

    @rx.event
    def set_form_date(self, value: str):
        self.form_date = value

    def _validate(self) -> str:
        if not self.form_patient_id:
            return "Please select a patient."
        if not self.form_doctor_id:
            return "Please select a doctor."
        if not self.form_test_type:
            return "Test type is required."
        if not self.form_date:
            return "Test date is required."
        try:
            datetime.strptime(self.form_date, "%Y-%m-%d")
        except ValueError:
            return "Invalid date format (YYYY-MM-DD)."
        if self.form_status == "Completed" and not self.form_result.strip():
            return "Result is required for completed tests."
        return ""

    @rx.event
    def save_lab(self):
        err = self._validate()
        if err:
            self.form_error = err
            return
        try:
            performed = datetime.strptime(self.form_date, "%Y-%m-%d")
            with SessionLocal() as db:
                if db.get(Patient, self.form_patient_id) is None:
                    self.form_error = "Selected patient not found."
                    return
                if db.get(User, self.form_doctor_id) is None:
                    self.form_error = "Selected doctor not found."
                    return
                if self.editing_id:
                    l = db.get(LaboratoryReport, self.editing_id)
                    if l is None:
                        self.form_error = "Lab report not found."
                        return
                else:
                    l = LaboratoryReport()
                    db.add(l)
                l.patient_id = self.form_patient_id
                l.doctor_id = self.form_doctor_id
                l.test_type = self.form_test_type
                l.test_name = self.form_test_name.strip() or self.form_test_type
                l.result = self.form_result.strip()
                l.reference_range = self.form_remarks.strip() or "Normal"
                l.status = self.form_status
                l.performed_on = performed
                db.commit()
            self.form_open = False
            self.success_message = "Laboratory report saved successfully."
            yield rx.toast.success("Lab report saved.")
            yield LaboratoryState.load_rows
        except Exception as e:
            logging.exception(f"save_lab: {e}")
            self.form_error = "Failed to save lab report."

    @rx.event
    async def handle_upload(self, files: list[rx.UploadFile]):
        import random as _r
        import string as _s

        if not files:
            return
        try:
            file = files[0]
            data = await file.read()
            upload_dir = rx.get_upload_dir()
            upload_dir.mkdir(parents=True, exist_ok=True)
            suffix = "".join(_r.choices(_s.ascii_lowercase + _s.digits, k=8))
            safe_name = f"labupload_{suffix}_{file.name}"
            (upload_dir / safe_name).write_bytes(data)
            self.form_upload_file = safe_name
            if self.editing_id:
                with SessionLocal() as db:
                    d = Document(
                        patient_id=self.form_patient_id,
                        title=f"lab_{self.editing_id}__{file.name}",
                        doc_type="Lab Upload",
                        file_path=safe_name,
                    )
                    db.add(d)
                    db.commit()
            yield rx.toast.success(f"Uploaded {file.name}.")
        except Exception as e:
            logging.exception(f"handle_upload: {e}")
            yield rx.toast.error("Upload failed.")

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
    def delete_lab(self):
        if not self.delete_id:
            return
        try:
            with SessionLocal() as db:
                l = db.get(LaboratoryReport, self.delete_id)
                if l is not None:
                    db.delete(l)
                    db.commit()
            self.delete_open = False
            self.delete_id = 0
            yield rx.toast.success("Lab report deleted.")
            yield LaboratoryState.load_rows
        except Exception as e:
            logging.exception(f"delete_lab: {e}")
            yield rx.toast.error("Failed to delete lab report.")

    @rx.event
    def download_pdf(self, row_id: int):
        row = next((r for r in self.rows if r["id"] == row_id), None)
        if row is None:
            return
        try:
            filename = generate_lab_report_pdf(
                {
                    "patient": row["patient"],
                    "doctor": row["doctor"],
                    "date": row["date"],
                    "test_type": row["test_type"],
                    "test_name": row["test_name"],
                    "result": row["result"],
                    "reference_range": row["remarks"],
                    "status": row["status"],
                    "remarks": row["remarks"],
                }
            )
            self.generated_pdf = filename
            return rx.download(
                url=f"/_upload/{filename}",
                filename=f"lab_report_{row['id']}.pdf",
            )
        except Exception as e:
            logging.exception(f"lab download_pdf: {e}")
            return rx.toast.error("Failed to generate PDF.")

    @rx.event
    def view_uploaded(self, row_id: int):
        row = next((r for r in self.rows if r["id"] == row_id), None)
        if row is None or not row["file_name"]:
            return rx.toast.error("No uploaded file for this report.")
        return rx.redirect(
            f"/_upload/{row['file_name']}",
            external=True,
        )

    @rx.event
    def print_page(self):
        return rx.call_script("window.print()")
