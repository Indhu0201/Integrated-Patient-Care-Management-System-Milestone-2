import reflex as rx

from app.components.layout import loading_overlay, page_shell
from app.components.modal import (
    INPUT_CLS,
    error_banner,
    form_field,
    modal,
    primary_btn,
    secondary_btn,
)
from app.states.medical_history_state import MedicalHistoryState


def _timeline_section(
    title: str, icon: str, rows: rx.Var, empty: str
) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon(icon, class_name="h-5 w-5 text-blue-600"),
            rx.el.h3(title, class_name="text-base font-semibold text-gray-900"),
            class_name="flex items-center gap-2 px-5 py-3 border-b border-gray-200",
        ),
        rx.cond(
            rows.length() > 0,
            rx.el.div(
                rx.foreach(
                    rows,
                    lambda r: rx.el.div(
                        rx.el.div(
                            rx.cond(
                                r["date"] != "",
                                rx.el.p(
                                    r["date"],
                                    class_name="text-xs font-medium text-gray-500 w-24 shrink-0",
                                ),
                                rx.el.p(
                                    "-",
                                    class_name="text-xs font-medium text-gray-500 w-24 shrink-0",
                                ),
                            ),
                            rx.el.div(
                                rx.el.p(
                                    r["title"],
                                    class_name="text-sm font-semibold text-gray-900",
                                ),
                                rx.el.p(
                                    r["detail"],
                                    class_name="text-xs text-gray-600 mt-0.5",
                                ),
                                rx.cond(
                                    r["extra"] != "",
                                    rx.el.p(
                                        r["extra"],
                                        class_name="text-xs text-blue-600 mt-0.5",
                                    ),
                                    rx.fragment(),
                                ),
                                class_name="flex-1",
                            ),
                            class_name="flex items-start gap-3 px-5 py-3 border-t border-gray-100 first:border-t-0",
                        ),
                    ),
                ),
                class_name="",
            ),
            rx.el.p(empty, class_name="px-5 py-4 text-xs text-gray-500"),
        ),
        class_name="bg-white rounded-lg border border-gray-200 overflow-hidden",
    )


def _patient_details() -> rx.Component:
    p = MedicalHistoryState.patient_info

    def kv(label: str, value: rx.Var) -> rx.Component:
        return rx.el.div(
            rx.el.p(
                label,
                class_name="text-xs text-gray-500 uppercase tracking-wide",
            ),
            rx.el.p(
                value, class_name="text-sm font-semibold text-gray-900 mt-0.5"
            ),
            class_name="p-3 bg-gray-50 rounded-lg",
        )

    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.icon("user", class_name="h-6 w-6 text-white"),
                class_name="h-14 w-14 rounded-full bg-blue-600 flex items-center justify-center shrink-0",
            ),
            rx.el.div(
                rx.el.h2(
                    p["name"],
                    class_name="text-xl font-bold text-gray-900",
                ),
                rx.el.p(
                    f"MRN: {p['mrn']} • {p['gender']} • Age {p['age']} • DOB {p['dob']}",
                    class_name="text-sm text-gray-500",
                ),
            ),
            class_name="flex items-center gap-4 mb-4",
        ),
        rx.el.div(
            kv("Blood Group", p["blood"]),
            kv("Phone", p["phone"]),
            kv("Email", p["email"]),
            kv("Address", p["address"]),
            kv("Emergency", p["emergency"]),
            class_name="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3",
        ),
        class_name="bg-white p-5 rounded-lg border border-gray-200",
    )


def _search_sidebar() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h3(
                "Find Patient",
                class_name="text-sm font-semibold text-gray-900",
            ),
            class_name="px-4 py-3 border-b border-gray-200",
        ),
        rx.el.div(
            rx.el.input(
                placeholder="Search by ID, MRN, or name...",
                default_value=MedicalHistoryState.search_query,
                on_change=MedicalHistoryState.set_search_query.debounce(200),
                class_name=INPUT_CLS,
            ),
            class_name="p-3 border-b border-gray-200",
        ),
        rx.el.div(
            rx.foreach(
                MedicalHistoryState.patient_results,
                lambda p: rx.el.button(
                    rx.el.div(
                        rx.el.p(
                            p["label"],
                            class_name="text-sm font-medium text-gray-900 truncate",
                        ),
                        rx.el.p(p["mrn"], class_name="text-xs text-gray-500"),
                        class_name="flex flex-col items-start",
                    ),
                    on_click=lambda: MedicalHistoryState.select_patient(
                        p["id"]
                    ),
                    class_name=rx.cond(
                        MedicalHistoryState.selected_patient_id == p["id"],
                        "w-full text-left px-4 py-2 bg-blue-50 border-l-4 border-blue-600",
                        "w-full text-left px-4 py-2 hover:bg-gray-50 border-l-4 border-transparent",
                    ),
                ),
            ),
            class_name="overflow-y-auto max-h-[65vh]",
        ),
        class_name="bg-white rounded-lg border border-gray-200 overflow-hidden",
    )


def _actions_bar() -> rx.Component:
    return rx.el.div(
        primary_btn(
            rx.icon("plus", class_name="h-4 w-4"),
            "Update Record",
            type="button",
            on_click=MedicalHistoryState.open_update_new,
        ),
        secondary_btn(
            rx.icon("printer", class_name="h-4 w-4"),
            "Print",
            type="button",
            on_click=MedicalHistoryState.print_page,
        ),
        secondary_btn(
            rx.icon("download", class_name="h-4 w-4"),
            "Download PDF",
            type="button",
            on_click=MedicalHistoryState.download_pdf,
        ),
        class_name="flex flex-wrap gap-2 justify-end",
    )


def _history_table() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon("history", class_name="h-5 w-5 text-blue-600"),
            rx.el.h3(
                "Medical History Entries",
                class_name="text-base font-semibold text-gray-900",
            ),
            class_name="flex items-center gap-2 px-5 py-3 border-b border-gray-200",
        ),
        rx.cond(
            MedicalHistoryState.history_entries.length() > 0,
            rx.el.div(
                rx.el.table(
                    rx.el.thead(
                        rx.el.tr(
                            rx.el.th(
                                "Onset",
                                class_name="px-4 py-2 text-left text-xs font-semibold text-gray-500 uppercase",
                            ),
                            rx.el.th(
                                "Condition",
                                class_name="px-4 py-2 text-left text-xs font-semibold text-gray-500 uppercase",
                            ),
                            rx.el.th(
                                "Notes",
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
                            MedicalHistoryState.history_entries,
                            lambda h: rx.el.tr(
                                rx.el.td(
                                    h["onset"],
                                    class_name="px-4 py-3 text-sm text-gray-600",
                                ),
                                rx.el.td(
                                    h["condition"],
                                    class_name="px-4 py-3 text-sm text-gray-900 font-medium",
                                ),
                                rx.el.td(
                                    rx.cond(h["notes"] != "", h["notes"], "—"),
                                    class_name="px-4 py-3 text-sm text-gray-600",
                                ),
                                rx.el.td(
                                    rx.el.div(
                                        rx.el.button(
                                            rx.icon(
                                                "pencil",
                                                class_name="h-3.5 w-3.5",
                                            ),
                                            on_click=lambda: (
                                                MedicalHistoryState.open_update_edit(
                                                    h["id"]
                                                )
                                            ),
                                            class_name="px-2 py-1.5 bg-blue-50 hover:bg-blue-100 text-blue-700 rounded-lg",
                                            title="Edit",
                                        ),
                                        rx.el.button(
                                            rx.icon(
                                                "trash-2",
                                                class_name="h-3.5 w-3.5",
                                            ),
                                            on_click=lambda: (
                                                MedicalHistoryState.delete_history_entry(
                                                    h["id"]
                                                )
                                            ),
                                            class_name="px-2 py-1.5 bg-red-50 hover:bg-red-100 text-red-700 rounded-lg",
                                            title="Delete",
                                        ),
                                        class_name="flex justify-end gap-1",
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
            ),
            rx.el.p(
                "No medical history entries yet.",
                class_name="px-5 py-4 text-xs text-gray-500",
            ),
        ),
        class_name="bg-white rounded-lg border border-gray-200 overflow-hidden",
    )


def _update_modal() -> rx.Component:
    return modal(
        MedicalHistoryState.update_open,
        rx.cond(
            MedicalHistoryState.update_edit_id != 0,
            "Edit Medical History",
            "Add Medical History",
        ).to(str),
        MedicalHistoryState.close_update,
        error_banner(MedicalHistoryState.update_error),
        form_field(
            "Condition *",
            rx.el.input(
                on_change=MedicalHistoryState.set_update_condition.debounce(
                    200
                ),
                default_value=MedicalHistoryState.update_condition,
                class_name=INPUT_CLS,
            ),
        ),
        rx.el.div(class_name="h-3"),
        form_field(
            "Onset Date *",
            rx.el.input(
                type="date",
                on_change=MedicalHistoryState.set_update_onset,
                default_value=MedicalHistoryState.update_onset,
                class_name=INPUT_CLS,
            ),
        ),
        rx.el.div(class_name="h-3"),
        form_field(
            "Notes",
            rx.el.textarea(
                rows="3",
                on_change=MedicalHistoryState.set_update_notes.debounce(200),
                default_value=MedicalHistoryState.update_notes,
                class_name=INPUT_CLS,
            ),
        ),
        rx.el.div(
            secondary_btn(
                "Cancel",
                type="button",
                on_click=MedicalHistoryState.close_update,
            ),
            primary_btn(
                rx.icon("save", class_name="h-4 w-4"),
                "Save",
                type="button",
                on_click=MedicalHistoryState.save_update,
            ),
            class_name="flex justify-end gap-2 mt-5",
        ),
    )


def medical_history_page() -> rx.Component:
    return page_shell(
        "Medical History",
        [("Home", "/dashboard"), ("Medical History", "/medical-history")],
        loading_overlay(MedicalHistoryState.loading),
        rx.el.div(
            rx.el.div(_search_sidebar(), class_name="lg:col-span-1"),
            rx.el.div(
                rx.cond(
                    MedicalHistoryState.has_patient,
                    rx.el.div(
                        _actions_bar(),
                        _patient_details(),
                        _timeline_section(
                            "Consultation History",
                            "stethoscope",
                            MedicalHistoryState.consultations,
                            "No consultations recorded.",
                        ),
                        _timeline_section(
                            "Diagnosis History",
                            "clipboard-list",
                            MedicalHistoryState.diagnoses,
                            "No diagnoses recorded.",
                        ),
                        _timeline_section(
                            "Prescription History",
                            "pill",
                            MedicalHistoryState.prescriptions,
                            "No prescriptions recorded.",
                        ),
                        _timeline_section(
                            "Laboratory Reports",
                            "test-tube",
                            MedicalHistoryState.labs,
                            "No lab reports recorded.",
                        ),
                        _timeline_section(
                            "Allergies",
                            "shield-alert",
                            MedicalHistoryState.allergies,
                            "No allergies on record.",
                        ),
                        _timeline_section(
                            "Medications",
                            "pill",
                            MedicalHistoryState.medications,
                            "No medications on record.",
                        ),
                        _history_table(),
                        class_name="flex flex-col gap-4",
                    ),
                    rx.el.div(
                        rx.icon(
                            "search",
                            class_name="h-10 w-10 text-gray-300 mx-auto",
                        ),
                        rx.el.p(
                            "Search and select a patient to view their full medical history.",
                            class_name="text-sm text-gray-500 mt-3 text-center",
                        ),
                        class_name="bg-white p-10 rounded-lg border border-gray-200 flex flex-col items-center",
                    ),
                ),
                class_name="lg:col-span-3",
            ),
            class_name="grid grid-cols-1 lg:grid-cols-4 gap-4",
        ),
        _update_modal(),
    )
