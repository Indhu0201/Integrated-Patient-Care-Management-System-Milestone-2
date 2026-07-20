"""Shared lookup helpers for patients and doctors."""

from __future__ import annotations

import logging
from typing import TypedDict

from app.database import Patient, SessionLocal, User


class PatientOption(TypedDict):
    id: int
    label: str
    mrn: str


class DoctorOption(TypedDict):
    id: int
    label: str


def load_patient_options() -> list[PatientOption]:
    try:
        with SessionLocal() as db:
            rows = (
                db.query(Patient)
                .order_by(Patient.last_name, Patient.first_name)
                .all()
            )
            return [
                {
                    "id": p.id,
                    "label": f"{p.first_name} {p.last_name} ({p.mrn})",
                    "mrn": p.mrn,
                }
                for p in rows
            ]
    except Exception as e:
        logging.exception(f"load_patient_options: {e}")
        return []


def load_doctor_options() -> list[DoctorOption]:
    try:
        with SessionLocal() as db:
            rows = (
                db.query(User)
                .filter(User.role == "doctor")
                .order_by(User.full_name)
                .all()
            )
            return [{"id": u.id, "label": u.full_name} for u in rows]
    except Exception as e:
        logging.exception(f"load_doctor_options: {e}")
        return []
