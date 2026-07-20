import reflex as rx

from app.components.layout import loading_overlay, page_shell
from app.components.modal import (
    INPUT_CLS,
    error_banner,
    form_field,
    primary_btn,
    secondary_btn,
    success_banner,
)
from app.states.reports_state import ReportsState


def _filter_bar() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h3(
                "Search & Filter",
                class_name="text-base font-semibold text-gray-900",
            ),
            rx.el.p(
                "Search by any combination of the fields below.",
                class_name="text-xs text-gray-500 mt-0.5",
            ),
            class_name="px-5 py-3 border-b border-gray-200",
        ),
        rx.el.div(
            form_field(
                "Patient ID (MRN)",
                rx.el.input(
                    placeholder="e.g. MRN10012",
                    default_value=ReportsState.filter_patient_id,
                    on_change=ReportsState.set_filter_patient_id.debounce(300),
                    class_name=INPUT_CLS,
                ),
            ),
            form_field(
                "Patient Name",
                rx.el.input(
                    placeholder="First or last name",
                    default_value=ReportsState.filter_patient_name,
                    on_change=ReportsState.set_filter_patient_name.debounce(
                        300
                    ),
                    class_name=INPUT_CLS,
                ),
            ),
            form_field(
                "Doctor",
                rx.el.input(
                    placeholder="Doctor name",
                    default_value=ReportsState.filter_doctor,
                    on_change=ReportsState.set_filter_doctor.debounce(300),
                    class_name=INPUT_CLS,
                ),
            ),
            form_field(
                "Diagnosis",
                rx.el.input(
                    placeholder="e.g. Migraine",
                    default_value=ReportsState.filter_diagnosis,
                    on_change=ReportsState.set_filter_diagnosis.debounce(300),
                    class_name=INPUT_CLS,
                ),
            ),
            form_field(
                "From Date",
                rx.el.input(
                    type="date",
                    default_value=ReportsState.filter_date_from,
                    on_change=ReportsState.set_filter_date_from,
                    class_name=INPUT_CLS,
                ),
            ),
            form_field(
                "To Date",
                rx.el.input(
                    type="date",
                    default_value=ReportsState.filter_date_to,
                    on_change=ReportsState.set_filter_date_to,
                    class_name=INPUT_CLS,
                ),
            ),
            class_name="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 p-5",
        ),
        rx.el.div(
            secondary_btn(
                rx.icon("x", class_name="h-4 w-4"),
                "Clear",
                type="button",
                on_click=ReportsState.clear_filters,
            ),
            primary_btn(
                rx.icon("search", class_name="h-4 w-4"),
                "Search",
                type="button",
                on_click=ReportsState.run_search,
            ),
            class_name="flex justify-end gap-2 px-5 py-3 border-t border-gray-200",
        ),
        class_name="bg-white rounded-lg border border-gray-200 overflow-hidden",
    )


def _results_list() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h3(
                "Matching Patients",
                class_name="text-base font-semibold text-gray-900",
            ),
            rx.el.p(
                f"{ReportsState.patient_hits.length()} result(s)",
                class_name="text-xs text-gray-500 mt-0.5",
            ),
            class_name="px-5 py-3 border-b border-gray-200",
        ),
        rx.cond(
            ReportsState.patient_hits.length() > 0,
            rx.el.div(
                rx.foreach(
                    ReportsState.patient_hits,
                    lambda h: rx.el.button(
                        rx.el.div(
                            rx.el.p(
                                h["name"],
                                class_name="text-sm font-semibold text-gray-900",
                            ),
                            rx.el.p(
                                h["subtitle"],
                                class_name="text-xs text-gray-500",
                            ),
                            class_name="flex flex-col items-start",
                        ),
                        on_click=lambda: ReportsState.select_patient(h["id"]),
                        class_name=rx.cond(
                            ReportsState.selected_patient_id == h["id"],
                            "w-full text-left px-4 py-3 border-l-4 border-blue-600 bg-blue-50",
                            "w-full text-left px-4 py-3 border-l-4 border-transparent hover:bg-gray-50 border-t border-gray-100 first:border-t-0",
                        ),
                    ),
                ),
                class_name="max-h-[50vh] overflow-y-auto",
            ),
            rx.el.p(
                "Run a search to see matching patients.",
                class_name="px-5 py-4 text-xs text-gray-500",
            ),
        ),
        class_name="bg-white rounded-lg border border-gray-200 overflow-hidden",
    )


def _timeline(title: str, icon: str, rows: rx.Var) -> rx.Component:
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
                        rx.el.p(
                            r["date"],
                            class_name="text-xs font-medium text-gray-500 w-24 shrink-0",
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
                )
            ),
            rx.el.p(
                "No records.", class_name="px-5 py-4 text-xs text-gray-500"
            ),
        ),
        class_name="bg-white rounded-lg border border-gray-200 overflow-hidden",
    )


def _patient_report() -> rx.Component:
    p = ReportsState.patient_info

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
                        f"MRN: {p['mrn']} • {p['gender']} • Age {p['age']}",
                        class_name="text-sm text-gray-500",
                    ),
                ),
                class_name="flex items-center gap-4",
            ),
            rx.el.div(
                secondary_btn(
                    rx.icon("printer", class_name="h-4 w-4"),
                    "Print Report",
                    type="button",
                    on_click=ReportsState.print_page,
                ),
                secondary_btn(
                    rx.icon("download", class_name="h-4 w-4"),
                    "Download PDF",
                    type="button",
                    on_click=ReportsState.download_pdf,
                ),
                primary_btn(
                    rx.icon("file-text", class_name="h-4 w-4"),
                    "Generate Medical Report",
                    type="button",
                    on_click=ReportsState.generate_medical_report,
                ),
                class_name="flex flex-wrap gap-2",
            ),
            class_name="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-4",
        ),
        rx.el.div(
            kv("Blood Group", p["blood"]),
            kv("Phone", p["phone"]),
            kv("Email", p["email"]),
            kv("Address", p["address"]),
            class_name="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3",
        ),
        class_name="bg-white p-5 rounded-lg border border-gray-200",
    )


def reports_page() -> rx.Component:
    return page_shell(
        "Reports & Search",
        [("Home", "/dashboard"), ("Reports & Search", "/reports")],
        loading_overlay(ReportsState.loading),
        error_banner(ReportsState.error),
        success_banner(ReportsState.success_message),
        _filter_bar(),
        rx.el.div(
            rx.el.div(_results_list(), class_name="lg:col-span-1"),
            rx.el.div(
                rx.cond(
                    ReportsState.has_patient,
                    rx.el.div(
                        _patient_report(),
                        _timeline(
                            "Consultation History",
                            "stethoscope",
                            ReportsState.consultations,
                        ),
                        _timeline(
                            "Prescription History",
                            "pill",
                            ReportsState.prescriptions,
                        ),
                        _timeline(
                            "Laboratory Reports",
                            "test-tube",
                            ReportsState.labs,
                        ),
                        class_name="flex flex-col gap-4",
                    ),
                    rx.el.div(
                        rx.icon(
                            "file-search",
                            class_name="h-10 w-10 text-gray-300 mx-auto",
                        ),
                        rx.el.p(
                            "Select a matching patient to view their full report.",
                            class_name="text-sm text-gray-500 mt-3 text-center",
                        ),
                        class_name="bg-white p-10 rounded-lg border border-gray-200 flex flex-col items-center",
                    ),
                ),
                class_name="lg:col-span-2",
            ),
            class_name="grid grid-cols-1 lg:grid-cols-3 gap-4",
        ),
    )
