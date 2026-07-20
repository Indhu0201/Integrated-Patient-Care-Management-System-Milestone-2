"""ReportLab-based PDF generation for prescriptions and lab reports."""

from __future__ import annotations

import logging
import random
import string
from datetime import datetime

import reflex as rx
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


def _new_filename(prefix: str) -> str:
    suffix = "".join(
        random.choices(string.ascii_lowercase + string.digits, k=8)
    )
    return f"{prefix}_{suffix}.pdf"


def _upload_path(filename: str) -> str:
    upload_dir = rx.get_upload_dir()
    upload_dir.mkdir(parents=True, exist_ok=True)
    # ReportLab requires a str filename, not a PosixPath.
    return str(upload_dir / filename)


def _kv_table(rows: list[tuple[str, str]]) -> Table:
    tbl = Table(rows, colWidths=[130, 380])
    tbl.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EFF6FF")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    return tbl


def _header(story: list, styles, subtitle: str) -> None:
    story.append(Paragraph("<b>IPCMS</b>", styles["Title"]))
    story.append(
        Paragraph("Integrated Patient Care Management System", styles["Italic"])
    )
    story.append(Paragraph(f"<b>{subtitle}</b>", styles["Heading2"]))
    story.append(
        Paragraph(
            f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
            styles["Normal"],
        )
    )
    story.append(Spacer(1, 14))


def generate_prescription_pdf(data: dict) -> str:
    """Write a prescription PDF into the upload dir and return the filename."""
    try:
        filename = _new_filename("prescription")
        path = _upload_path(filename)
        doc = SimpleDocTemplate(path, pagesize=letter)
        styles = getSampleStyleSheet()
        story: list = []
        _header(story, styles, "Medical Prescription")
        story.append(
            _kv_table(
                [
                    ("Patient", data.get("patient", "")),
                    ("Doctor", data.get("doctor", "")),
                    ("Date", data.get("date", "")),
                ]
            )
        )
        story.append(Spacer(1, 14))
        story.append(Paragraph("<b>Rx</b>", styles["Heading3"]))
        story.append(
            _kv_table(
                [
                    ("Medication", data.get("medication", "")),
                    ("Dosage", data.get("dosage", "")),
                    ("Frequency", data.get("frequency", "")),
                    ("Duration", data.get("duration", "")),
                    ("Instructions", data.get("instructions", "")),
                ]
            )
        )
        story.append(Spacer(1, 40))
        story.append(
            Paragraph(
                "_________________________<br/>Doctor's Signature",
                styles["Normal"],
            )
        )
        doc.build(story)
        return filename
    except Exception as e:
        logging.exception(f"Prescription PDF generation failed: {e}")
        raise


_CELL_STYLE = getSampleStyleSheet()["BodyText"]


def _timeline_table(rows: list[dict]) -> Table | None:
    """Render a list of timeline dicts (date/title/detail/extra) as a table."""
    if not rows:
        return None
    header = ["Date", "Title", "Detail", "By / Status"]
    data = [header]
    for r in rows:
        data.append(
            [
                r.get("date", "") or "-",
                Paragraph(r.get("title", "") or "-", _CELL_STYLE),
                Paragraph(r.get("detail", "") or "-", _CELL_STYLE),
                Paragraph(r.get("extra", "") or "-", _CELL_STYLE),
            ]
        )
    tbl = Table(data, colWidths=[70, 130, 200, 110])
    tbl.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1D4ED8")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#94A3B8")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [colors.white, colors.HexColor("#F1F5F9")],
                ),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return tbl


def _patient_info_block(patient: dict) -> Table:
    return _kv_table(
        [
            ("Patient", patient.get("name", "")),
            ("MRN", patient.get("mrn", "")),
            (
                "Gender / Age",
                f"{patient.get('gender', '')} / {patient.get('age', '')}",
            ),
            ("Date of Birth", patient.get("dob", "")),
            ("Blood Group", patient.get("blood", "-")),
            ("Phone", patient.get("phone", "-")),
            ("Email", patient.get("email", "-")),
            ("Address", patient.get("address", "-")),
            ("Emergency Contact", patient.get("emergency", "-")),
        ]
    )


def _section(
    story: list, styles, title: str, rows: list[dict], empty_note: str
) -> None:
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"<b>{title}</b>", styles["Heading3"]))
    tbl = _timeline_table(rows)
    if tbl is None:
        story.append(Paragraph(empty_note, styles["Italic"]))
    else:
        story.append(tbl)


def generate_medical_history_pdf(data: dict) -> str:
    """Comprehensive medical history PDF."""
    try:
        filename = _new_filename("medical_history")
        path = _upload_path(filename)
        doc = SimpleDocTemplate(path, pagesize=letter)
        styles = getSampleStyleSheet()
        story: list = []
        _header(story, styles, "Complete Medical History")
        story.append(_patient_info_block(data.get("patient", {})))
        _section(
            story,
            styles,
            "Medical History Entries",
            [
                {
                    "date": h.get("onset", ""),
                    "title": h.get("condition", ""),
                    "detail": h.get("notes", ""),
                    "extra": "",
                }
                for h in data.get("history", [])
            ],
            "No medical history entries recorded.",
        )
        _section(
            story,
            styles,
            "Consultation History",
            data.get("consultations", []),
            "No consultations recorded.",
        )
        _section(
            story,
            styles,
            "Diagnosis History",
            data.get("diagnoses", []),
            "No diagnoses recorded.",
        )
        _section(
            story,
            styles,
            "Prescription History",
            data.get("prescriptions", []),
            "No prescriptions recorded.",
        )
        _section(
            story,
            styles,
            "Laboratory Reports",
            data.get("labs", []),
            "No lab reports recorded.",
        )
        _section(
            story,
            styles,
            "Allergies",
            data.get("allergies", []),
            "No allergies on record.",
        )
        _section(
            story,
            styles,
            "Medications",
            data.get("medications", []),
            "No medications on record.",
        )
        story.append(Spacer(1, 30))
        story.append(
            Paragraph(
                "This document is generated by IPCMS for administrative use.",
                styles["Italic"],
            )
        )
        doc.build(story)
        return filename
    except Exception as e:
        logging.exception(f"Medical history PDF generation failed: {e}")
        raise


def generate_patient_report_pdf(data: dict) -> str:
    """Consolidated patient report PDF used by Reports & Search."""
    try:
        filename = _new_filename("patient_report")
        path = _upload_path(filename)
        doc = SimpleDocTemplate(path, pagesize=letter)
        styles = getSampleStyleSheet()
        story: list = []
        _header(story, styles, "Consolidated Patient Report")
        story.append(_patient_info_block(data.get("patient", {})))
        _section(
            story,
            styles,
            "Consultation History",
            data.get("consultations", []),
            "No consultations recorded.",
        )
        _section(
            story,
            styles,
            "Prescription History",
            data.get("prescriptions", []),
            "No prescriptions recorded.",
        )
        _section(
            story,
            styles,
            "Laboratory Reports",
            data.get("labs", []),
            "No lab reports recorded.",
        )
        story.append(Spacer(1, 30))
        story.append(
            Paragraph(
                "_________________________<br/>Authorized Signature",
                styles["Normal"],
            )
        )
        doc.build(story)
        return filename
    except Exception as e:
        logging.exception(f"Patient report PDF generation failed: {e}")
        raise


def generate_ehr_record_pdf(data: dict) -> str:
    """Generate a complete EHR record PDF for one selected patient."""
    try:
        filename = _new_filename("ehr_record")
        path = _upload_path(filename)
        doc = SimpleDocTemplate(path, pagesize=letter)
        styles = getSampleStyleSheet()
        story: list = []
        _header(story, styles, "Electronic Health Record")

        patient = data.get("patient", {})
        story.append(_patient_info_block(patient))

        story.append(Spacer(1, 12))
        story.append(Paragraph("<b>Medical Summary</b>", styles["Heading3"]))
        summary = data.get("summary", {})
        story.append(
            _kv_table(
                [
                    ("Height (cm)", summary.get("height_cm", "-")),
                    ("Weight (kg)", summary.get("weight_kg", "-")),
                    ("BMI", summary.get("bmi", "-")),
                    ("Smoking", summary.get("smoking", "-")),
                    ("Alcohol", summary.get("alcohol", "-")),
                    ("Chronic Diseases", summary.get("chronic_diseases", "-")),
                    ("Remarks", summary.get("remarks", "-")),
                ]
            )
        )

        _section(
            story,
            styles,
            "Diagnosis History",
            data.get("diagnoses", []),
            "No diagnosis history recorded.",
        )
        _section(
            story,
            styles,
            "Allergies",
            data.get("allergies", []),
            "No allergies recorded.",
        )
        _section(
            story,
            styles,
            "Current Medications",
            data.get("medications", []),
            "No current medications recorded.",
        )
        _section(
            story,
            styles,
            "Laboratory Reports",
            data.get("labs", []),
            "No laboratory reports recorded.",
        )
        _section(
            story,
            styles,
            "Documents",
            data.get("documents", []),
            "No documents recorded.",
        )
        story.append(Spacer(1, 20))
        story.append(
            Paragraph(
                "This document is generated by IPCMS for authorized administrative use.",
                styles["Italic"],
            )
        )
        doc.build(story)
        return filename
    except Exception as e:
        logging.exception(f"EHR record PDF generation failed: {e}")
        raise


def generate_lab_report_pdf(data: dict) -> str:
    try:
        filename = _new_filename("lab_report")
        path = _upload_path(filename)
        doc = SimpleDocTemplate(path, pagesize=letter)
        styles = getSampleStyleSheet()
        story: list = []
        _header(story, styles, "Laboratory Report")
        story.append(
            _kv_table(
                [
                    ("Patient", data.get("patient", "")),
                    ("Doctor", data.get("doctor", "")),
                    ("Date", data.get("date", "")),
                ]
            )
        )
        story.append(Spacer(1, 14))
        story.append(Paragraph("<b>Test Details</b>", styles["Heading3"]))
        story.append(
            _kv_table(
                [
                    ("Test Type", data.get("test_type", "")),
                    ("Test Name", data.get("test_name", "")),
                    ("Result", data.get("result", "")),
                    ("Reference Range", data.get("reference_range", "Normal")),
                    ("Status", data.get("status", "")),
                    ("Remarks", data.get("remarks", "")),
                ]
            )
        )
        story.append(Spacer(1, 40))
        story.append(
            Paragraph(
                "_________________________<br/>Lab Technician",
                styles["Normal"],
            )
        )
        doc.build(story)
        return filename
    except Exception as e:
        logging.exception(f"Lab report PDF generation failed: {e}")
        raise
