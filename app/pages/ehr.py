import reflex as rx

from app.components.layout import loading_overlay, page_shell
from app.components.modal import (
    INPUT_CLS,
    LABEL_CLS,
    SELECT_CLS,
    confirm_dialog,
    danger_btn,
    error_banner,
    form_field,
    modal,
    primary_btn,
    secondary_btn,
)
from app.states.ehr_state import EHRState


def _patient_sidebar() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h3(
                "Patients", class_name="text-sm font-semibold text-gray-900"
            ),
            rx.el.p(
                f"{EHRState.patient_options.length()} total",
                class_name="text-xs text-gray-500",
            ),
            class_name="px-4 py-3 border-b border-gray-200",
        ),
        rx.el.div(
            rx.el.input(
                placeholder="Search patients...",
                default_value=EHRState.patient_search,
                on_change=EHRState.set_patient_search.debounce(200),
                class_name=INPUT_CLS,
            ),
            class_name="p-3 border-b border-gray-200",
        ),
        rx.el.div(
            rx.foreach(
                EHRState.filtered_patient_options,
                lambda p: rx.el.button(
                    rx.el.div(
                        rx.el.p(
                            p["label"],
                            class_name="text-sm font-medium text-gray-900 truncate",
                        ),
                        rx.el.p(p["mrn"], class_name="text-xs text-gray-500"),
                        class_name="flex flex-col items-start",
                    ),
                    on_click=lambda: EHRState.select_patient(p["id"]),
                    class_name=rx.cond(
                        EHRState.selected_patient_id == p["id"],
                        "w-full text-left px-4 py-2 bg-blue-50 border-l-4 border-blue-600",
                        "w-full text-left px-4 py-2 hover:bg-gray-50 border-l-4 border-transparent",
                    ),
                ),
            ),
            class_name="overflow-y-auto max-h-[70vh]",
        ),
        class_name="bg-white rounded-lg border border-gray-200 overflow-hidden",
    )


def _header_card() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.icon("user", class_name="h-6 w-6 text-white"),
                    class_name="h-14 w-14 rounded-full bg-blue-600 flex items-center justify-center shrink-0",
                ),
                rx.el.div(
                    rx.el.h2(
                        EHRState.patient_name,
                        class_name="text-xl font-bold text-gray-900",
                    ),
                    rx.el.p(
                        f"MRN: {EHRState.patient_mrn} • {EHRState.patient_gender} • DOB: {EHRState.patient_dob}",
                        class_name="text-sm text-gray-500",
                    ),
                    rx.el.p(
                        f"Blood: {EHRState.patient_blood} • {EHRState.patient_phone} • {EHRState.patient_email}",
                        class_name="text-xs text-gray-500 mt-0.5",
                    ),
                    rx.el.p(
                        f"Address: {EHRState.patient_address} • Emergency: {EHRState.patient_emergency}",
                        class_name="text-xs text-gray-500 mt-0.5",
                    ),
                ),
                class_name="flex items-center gap-4",
            ),
            rx.el.div(
                primary_btn(
                    rx.icon("pencil", class_name="h-4 w-4"),
                    "Edit Record",
                    on_click=EHRState.open_edit_summary,
                    type="button",
                ),
                secondary_btn(
                    rx.icon("printer", class_name="h-4 w-4"),
                    "Print Record",
                    on_click=EHRState.print_record,
                    type="button",
                ),
                secondary_btn(
                    rx.icon("download", class_name="h-4 w-4"),
                    "Download Record",
                    on_click=EHRState.download_record,
                    type="button",
                ),
                class_name="flex flex-wrap gap-2",
            ),
            class_name="flex flex-col md:flex-row md:items-center md:justify-between gap-4 p-5",
        ),
        class_name="bg-white rounded-lg border border-gray-200",
    )


def _summary_tab() -> rx.Component:
    def stat(label: str, value: rx.Var) -> rx.Component:
        return rx.el.div(
            rx.el.p(
                label,
                class_name="text-xs text-gray-500 uppercase tracking-wide",
            ),
            rx.el.p(
                value, class_name="text-base font-semibold text-gray-900 mt-1"
            ),
            class_name="p-4 bg-gray-50 rounded-lg border border-gray-200",
        )

    return rx.el.div(
        rx.el.div(
            stat(
                "Height (cm)",
                rx.cond(
                    EHRState.summary["height_cm"] != "",
                    EHRState.summary["height_cm"],
                    "—",
                ),
            ),
            stat(
                "Weight (kg)",
                rx.cond(
                    EHRState.summary["weight_kg"] != "",
                    EHRState.summary["weight_kg"],
                    "—",
                ),
            ),
            stat(
                "BMI",
                rx.cond(
                    EHRState.summary["bmi"] != "", EHRState.summary["bmi"], "—"
                ),
            ),
            stat("Smoking", EHRState.summary["smoking"]),
            stat("Alcohol", EHRState.summary["alcohol"]),
            class_name="grid grid-cols-2 md:grid-cols-5 gap-3",
        ),
        rx.el.div(
            rx.el.p(
                "Chronic Diseases",
                class_name="text-xs text-gray-500 uppercase tracking-wide",
            ),
            rx.el.p(
                rx.cond(
                    EHRState.summary["chronic_diseases"] != "",
                    EHRState.summary["chronic_diseases"],
                    "None recorded",
                ),
                class_name="text-sm text-gray-800 mt-1",
            ),
            class_name="p-4 bg-gray-50 rounded-lg border border-gray-200 mt-3",
        ),
        rx.el.div(
            rx.el.p(
                "Remarks",
                class_name="text-xs text-gray-500 uppercase tracking-wide",
            ),
            rx.el.p(
                rx.cond(
                    EHRState.summary["remarks"] != "",
                    EHRState.summary["remarks"],
                    "—",
                ),
                class_name="text-sm text-gray-800 mt-1",
            ),
            class_name="p-4 bg-gray-50 rounded-lg border border-gray-200 mt-3",
        ),
        class_name="p-5",
    )


def _dx_tab() -> rx.Component:
    return rx.el.div(
        rx.el.table(
            rx.el.thead(
                rx.el.tr(
                    rx.el.th(
                        "Date",
                        class_name="px-4 py-2 text-left text-xs font-semibold text-gray-500 uppercase",
                    ),
                    rx.el.th(
                        "Diagnosis",
                        class_name="px-4 py-2 text-left text-xs font-semibold text-gray-500 uppercase",
                    ),
                    rx.el.th(
                        "Notes",
                        class_name="px-4 py-2 text-left text-xs font-semibold text-gray-500 uppercase",
                    ),
                ),
                class_name="bg-gray-50",
            ),
            rx.el.tbody(
                rx.foreach(
                    EHRState.diagnoses,
                    lambda d: rx.el.tr(
                        rx.el.td(
                            d["date"],
                            class_name="px-4 py-3 text-sm text-gray-600",
                        ),
                        rx.el.td(
                            d["diagnosis"],
                            class_name="px-4 py-3 text-sm text-gray-900 font-medium",
                        ),
                        rx.el.td(
                            rx.cond(d["notes"] != "", d["notes"], "—"),
                            class_name="px-4 py-3 text-sm text-gray-600",
                        ),
                        class_name="border-t border-gray-100 hover:bg-gray-50",
                    ),
                )
            ),
            class_name="table-auto w-full",
        ),
        class_name="overflow-x-auto",
    )


def _allergies_tab() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            primary_btn(
                rx.icon("plus", class_name="h-4 w-4"),
                "Add Allergy",
                on_click=EHRState.open_add_allergy,
                type="button",
            ),
            class_name="flex justify-end p-4",
        ),
        rx.el.table(
            rx.el.thead(
                rx.el.tr(
                    rx.el.th(
                        "Allergen",
                        class_name="px-4 py-2 text-left text-xs font-semibold text-gray-500 uppercase",
                    ),
                    rx.el.th(
                        "Severity",
                        class_name="px-4 py-2 text-left text-xs font-semibold text-gray-500 uppercase",
                    ),
                    rx.el.th(
                        "Reaction",
                        class_name="px-4 py-2 text-left text-xs font-semibold text-gray-500 uppercase",
                    ),
                    rx.el.th(
                        "Actions",
                        class_name="px-4 py-2 text-right text-xs font-semibold text-gray-500 uppercase",
                    ),
                ),
                class_name="bg-gray-50",
            ),
            rx.el.tbody(
                rx.foreach(
                    EHRState.allergies,
                    lambda a: rx.el.tr(
                        rx.el.td(
                            a["allergen"],
                            class_name="px-4 py-3 text-sm text-gray-900 font-medium",
                        ),
                        rx.el.td(
                            a["severity"],
                            class_name="px-4 py-3 text-sm text-gray-600",
                        ),
                        rx.el.td(
                            rx.cond(a["reaction"] != "", a["reaction"], "—"),
                            class_name="px-4 py-3 text-sm text-gray-600",
                        ),
                        rx.el.td(
                            rx.el.div(
                                rx.el.button(
                                    rx.icon("pencil", class_name="h-3.5 w-3.5"),
                                    "Edit",
                                    on_click=lambda: EHRState.open_edit_allergy(
                                        a["id"]
                                    ),
                                    class_name="px-3 py-1.5 bg-blue-50 border border-blue-200 text-blue-700 rounded-lg text-xs font-medium hover:bg-blue-100 flex items-center gap-1",
                                ),
                                danger_btn(
                                    rx.icon(
                                        "trash-2", class_name="h-3.5 w-3.5"
                                    ),
                                    "Delete",
                                    on_click=lambda: EHRState.delete_allergy(
                                        a["id"]
                                    ),
                                    type="button",
                                ),
                                class_name="flex justify-end gap-2",
                            ),
                            class_name="px-4 py-3",
                        ),
                        class_name="border-t border-gray-100 hover:bg-gray-50",
                    ),
                )
            ),
            class_name="table-auto w-full",
        ),
        class_name="overflow-x-auto",
    )


def _meds_tab() -> rx.Component:
    return rx.el.table(
        rx.el.thead(
            rx.el.tr(
                rx.el.th(
                    "Medicine",
                    class_name="px-4 py-2 text-left text-xs font-semibold text-gray-500 uppercase",
                ),
                rx.el.th(
                    "Dosage",
                    class_name="px-4 py-2 text-left text-xs font-semibold text-gray-500 uppercase",
                ),
                rx.el.th(
                    "Frequency",
                    class_name="px-4 py-2 text-left text-xs font-semibold text-gray-500 uppercase",
                ),
                rx.el.th(
                    "Start Date",
                    class_name="px-4 py-2 text-left text-xs font-semibold text-gray-500 uppercase",
                ),
            ),
            class_name="bg-gray-50",
        ),
        rx.el.tbody(
            rx.foreach(
                EHRState.medications,
                lambda m: rx.el.tr(
                    rx.el.td(
                        m["name"],
                        class_name="px-4 py-3 text-sm text-gray-900 font-medium",
                    ),
                    rx.el.td(
                        m["dosage"],
                        class_name="px-4 py-3 text-sm text-gray-600",
                    ),
                    rx.el.td(
                        m["frequency"],
                        class_name="px-4 py-3 text-sm text-gray-600",
                    ),
                    rx.el.td(
                        m["started_on"],
                        class_name="px-4 py-3 text-sm text-gray-600",
                    ),
                    class_name="border-t border-gray-100 hover:bg-gray-50",
                ),
            )
        ),
        class_name="table-auto w-full",
    )


def _labs_tab() -> rx.Component:
    return rx.el.table(
        rx.el.thead(
            rx.el.tr(
                rx.el.th(
                    "Test",
                    class_name="px-4 py-2 text-left text-xs font-semibold text-gray-500 uppercase",
                ),
                rx.el.th(
                    "Date",
                    class_name="px-4 py-2 text-left text-xs font-semibold text-gray-500 uppercase",
                ),
                rx.el.th(
                    "Result",
                    class_name="px-4 py-2 text-left text-xs font-semibold text-gray-500 uppercase",
                ),
                rx.el.th(
                    "Status",
                    class_name="px-4 py-2 text-left text-xs font-semibold text-gray-500 uppercase",
                ),
            ),
            class_name="bg-gray-50",
        ),
        rx.el.tbody(
            rx.foreach(
                EHRState.labs,
                lambda l: rx.el.tr(
                    rx.el.td(
                        l["test"],
                        class_name="px-4 py-3 text-sm text-gray-900 font-medium",
                    ),
                    rx.el.td(
                        l["date"], class_name="px-4 py-3 text-sm text-gray-600"
                    ),
                    rx.el.td(
                        l["result"],
                        class_name="px-4 py-3 text-sm text-gray-600",
                    ),
                    rx.el.td(
                        l["status"],
                        class_name="px-4 py-3 text-sm text-gray-600",
                    ),
                    class_name="border-t border-gray-100 hover:bg-gray-50",
                ),
            )
        ),
        class_name="table-auto w-full",
    )


def _docs_tab() -> rx.Component:
    return rx.el.table(
        rx.el.thead(
            rx.el.tr(
                rx.el.th(
                    "Title",
                    class_name="px-4 py-2 text-left text-xs font-semibold text-gray-500 uppercase",
                ),
                rx.el.th(
                    "Type",
                    class_name="px-4 py-2 text-left text-xs font-semibold text-gray-500 uppercase",
                ),
                rx.el.th(
                    "Uploaded On",
                    class_name="px-4 py-2 text-left text-xs font-semibold text-gray-500 uppercase",
                ),
            ),
            class_name="bg-gray-50",
        ),
        rx.el.tbody(
            rx.foreach(
                EHRState.documents,
                lambda d: rx.el.tr(
                    rx.el.td(
                        d["title"],
                        class_name="px-4 py-3 text-sm text-gray-900 font-medium",
                    ),
                    rx.el.td(
                        d["doc_type"],
                        class_name="px-4 py-3 text-sm text-gray-600",
                    ),
                    rx.el.td(
                        d["uploaded_on"],
                        class_name="px-4 py-3 text-sm text-gray-600",
                    ),
                    class_name="border-t border-gray-100 hover:bg-gray-50",
                ),
            )
        ),
        class_name="table-auto w-full",
    )


def _section_card(
    title: str,
    icon: str,
    content: rx.Component,
    has_rows: rx.Var,
    empty_message: str,
) -> rx.Component:
    return rx.el.section(
        rx.el.div(
            rx.icon(icon, class_name="h-5 w-5 text-blue-600"),
            rx.el.h3(title, class_name="text-base font-semibold text-gray-900"),
            class_name="flex items-center gap-2 px-5 py-3 border-b border-gray-200",
        ),
        rx.cond(
            has_rows,
            content,
            rx.el.div(
                rx.icon("inbox", class_name="h-5 w-5 text-gray-300"),
                rx.el.p(empty_message, class_name="text-sm text-gray-500"),
                class_name="flex items-center gap-2 px-5 py-6",
            ),
        ),
        class_name="bg-white rounded-lg border border-gray-200 overflow-hidden",
    )


def _consolidated_sections() -> rx.Component:
    return rx.el.div(
        _section_card(
            "Medical Summary",
            "clipboard-list",
            _summary_tab(),
            rx.cond(
                (EHRState.summary["height_cm"] != "")
                | (EHRState.summary["weight_kg"] != "")
                | (EHRState.summary["chronic_diseases"] != "")
                | (EHRState.summary["remarks"] != ""),
                True,
                False,
            ),
            "No medical summary recorded yet.",
        ),
        _section_card(
            "Diagnosis History",
            "history",
            _dx_tab(),
            EHRState.diagnoses.length() > 0,
            "No diagnosis history recorded.",
        ),
        _section_card(
            "Allergies",
            "shield-alert",
            _allergies_tab(),
            EHRState.allergies.length() > 0,
            "No allergies recorded.",
        ),
        _section_card(
            "Current Medications",
            "pill",
            _meds_tab(),
            EHRState.medications.length() > 0,
            "No current medications recorded.",
        ),
        _section_card(
            "Laboratory Reports",
            "test-tube",
            _labs_tab(),
            EHRState.labs.length() > 0,
            "No laboratory reports recorded.",
        ),
        _section_card(
            "Documents",
            "file-text",
            _docs_tab(),
            EHRState.documents.length() > 0,
            "No documents recorded.",
        ),
        class_name="flex flex-col gap-4",
    )


def _summary_modal() -> rx.Component:
    yes_no = ["No", "Yes", "Former"]
    return modal(
        EHRState.edit_summary_open,
        "Edit Medical Summary",
        EHRState.close_edit_summary,
        rx.el.form(
            error_banner(EHRState.summary_error),
            rx.el.div(
                form_field(
                    "Height (cm)",
                    rx.el.input(
                        name="height_cm",
                        type="number",
                        step="0.1",
                        default_value=EHRState.summary["height_cm"],
                        key=EHRState.summary["height_cm"],
                        class_name=INPUT_CLS,
                    ),
                ),
                form_field(
                    "Weight (kg)",
                    rx.el.input(
                        name="weight_kg",
                        type="number",
                        step="0.1",
                        default_value=EHRState.summary["weight_kg"],
                        key=EHRState.summary["weight_kg"],
                        class_name=INPUT_CLS,
                    ),
                ),
                form_field(
                    "Smoking",
                    rx.el.select(
                        rx.foreach(yes_no, lambda o: rx.el.option(o, value=o)),
                        name="smoking",
                        default_value=EHRState.summary["smoking"],
                        key=EHRState.summary["smoking"],
                        class_name=SELECT_CLS,
                    ),
                ),
                form_field(
                    "Alcohol",
                    rx.el.select(
                        rx.foreach(yes_no, lambda o: rx.el.option(o, value=o)),
                        name="alcohol",
                        default_value=EHRState.summary["alcohol"],
                        key=EHRState.summary["alcohol"],
                        class_name=SELECT_CLS,
                    ),
                ),
                class_name="grid grid-cols-2 gap-4 mb-4",
            ),
            form_field(
                "Chronic Diseases",
                rx.el.textarea(
                    name="chronic_diseases",
                    default_value=EHRState.summary["chronic_diseases"],
                    key=EHRState.summary["chronic_diseases"],
                    rows="2",
                    class_name=INPUT_CLS,
                ),
            ),
            rx.el.div(class_name="h-3"),
            form_field(
                "Remarks",
                rx.el.textarea(
                    name="remarks",
                    default_value=EHRState.summary["remarks"],
                    key=EHRState.summary["remarks"],
                    rows="3",
                    class_name=INPUT_CLS,
                ),
            ),
            rx.el.div(
                secondary_btn(
                    "Cancel",
                    type="button",
                    on_click=EHRState.close_edit_summary,
                ),
                primary_btn(
                    rx.icon("save", class_name="h-4 w-4"),
                    "Save Summary",
                    type="submit",
                ),
                class_name="flex justify-end gap-2 mt-5",
            ),
            on_submit=EHRState.save_summary,
        ),
    )


def _allergy_modal() -> rx.Component:
    severities = ["Mild", "Moderate", "Severe"]
    return modal(
        EHRState.allergy_modal_open,
        rx.cond(
            EHRState.allergy_edit_id != 0, "Edit Allergy", "Add Allergy"
        ).to(str),
        EHRState.close_allergy_modal,
        rx.el.form(
            error_banner(EHRState.allergy_error),
            form_field(
                "Allergen",
                rx.el.input(
                    name="allergen",
                    default_value=EHRState.allergy_form["allergen"],
                    key=EHRState.allergy_form["allergen"],
                    class_name=INPUT_CLS,
                ),
            ),
            rx.el.div(class_name="h-3"),
            form_field(
                "Severity",
                rx.el.select(
                    rx.foreach(severities, lambda s: rx.el.option(s, value=s)),
                    name="severity",
                    default_value=EHRState.allergy_form["severity"],
                    key=EHRState.allergy_form["severity"],
                    class_name=SELECT_CLS,
                ),
            ),
            rx.el.div(class_name="h-3"),
            form_field(
                "Reaction",
                rx.el.textarea(
                    name="reaction",
                    default_value=EHRState.allergy_form["reaction"],
                    key=EHRState.allergy_form["reaction"],
                    rows="2",
                    class_name=INPUT_CLS,
                ),
            ),
            rx.el.div(
                secondary_btn(
                    "Cancel",
                    type="button",
                    on_click=EHRState.close_allergy_modal,
                ),
                primary_btn(
                    rx.icon("save", class_name="h-4 w-4"),
                    "Save",
                    type="submit",
                ),
                class_name="flex justify-end gap-2 mt-5",
            ),
            on_submit=EHRState.save_allergy,
        ),
    )


def ehr_page() -> rx.Component:
    return page_shell(
        "Electronic Health Records",
        [("Home", "/dashboard"), ("EHR", "/ehr")],
        loading_overlay(EHRState.loading),
        rx.el.div(
            rx.el.div(_patient_sidebar(), class_name="lg:col-span-1"),
            rx.el.div(
                _header_card(),
                _consolidated_sections(),
                class_name="lg:col-span-3 flex flex-col gap-4",
            ),
            class_name="grid grid-cols-1 lg:grid-cols-4 gap-4",
        ),
        _summary_modal(),
        _allergy_modal(),
    )
