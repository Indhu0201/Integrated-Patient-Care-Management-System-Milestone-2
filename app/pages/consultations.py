import reflex as rx

from app.components.layout import loading_overlay, page_shell
from app.components.modal import (
    INPUT_CLS,
    SELECT_CLS,
    confirm_dialog,
    danger_btn,
    error_banner,
    form_field,
    modal,
    primary_btn,
    secondary_btn,
    success_banner,
)
from app.states.consultations_state import ConsultationsState


def _toolbar() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.input(
                placeholder="Search by patient, doctor, diagnosis...",
                default_value=ConsultationsState.search_query,
                on_change=ConsultationsState.set_search_query.debounce(300),
                class_name=INPUT_CLS + " min-w-72",
            ),
            secondary_btn(
                rx.icon("arrow-up-down", class_name="h-4 w-4"),
                rx.cond(ConsultationsState.sort_desc, "Newest", "Oldest"),
                type="button",
                on_click=ConsultationsState.toggle_sort,
            ),
            class_name="flex flex-wrap gap-2 items-center",
        ),
        primary_btn(
            rx.icon("plus", class_name="h-4 w-4"),
            "New Consultation",
            type="button",
            on_click=ConsultationsState.open_new,
        ),
        class_name="flex flex-wrap items-center justify-between gap-3 p-4 border-b border-gray-200",
    )


def _table() -> rx.Component:
    return rx.el.div(
        rx.el.table(
            rx.el.thead(
                rx.el.tr(
                    rx.el.th(
                        "Patient",
                        class_name="px-4 py-2 text-left text-xs font-semibold text-gray-500 uppercase",
                    ),
                    rx.el.th(
                        "Doctor",
                        class_name="px-4 py-2 text-left text-xs font-semibold text-gray-500 uppercase hidden md:table-cell",
                    ),
                    rx.el.th(
                        "Date",
                        class_name="px-4 py-2 text-left text-xs font-semibold text-gray-500 uppercase",
                    ),
                    rx.el.th(
                        "Diagnosis",
                        class_name="px-4 py-2 text-left text-xs font-semibold text-gray-500 uppercase hidden lg:table-cell",
                    ),
                    rx.el.th(
                        "Status",
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
                    ConsultationsState.page_rows,
                    lambda r: rx.el.tr(
                        rx.el.td(
                            r["patient"],
                            class_name="px-4 py-3 text-sm text-gray-900 font-medium",
                        ),
                        rx.el.td(
                            r["doctor"],
                            class_name="px-4 py-3 text-sm text-gray-600 hidden md:table-cell",
                        ),
                        rx.el.td(
                            r["date"],
                            class_name="px-4 py-3 text-sm text-gray-600",
                        ),
                        rx.el.td(
                            r["diagnosis"],
                            class_name="px-4 py-3 text-sm text-gray-600 hidden lg:table-cell",
                        ),
                        rx.el.td(
                            rx.el.span(
                                r["status"],
                                class_name="px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-700",
                            ),
                            class_name="px-4 py-3",
                        ),
                        rx.el.td(
                            rx.el.div(
                                rx.el.button(
                                    rx.icon("eye", class_name="h-3.5 w-3.5"),
                                    on_click=lambda: (
                                        ConsultationsState.open_view(r["id"])
                                    ),
                                    class_name="px-2 py-1.5 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg",
                                    title="View",
                                ),
                                rx.el.button(
                                    rx.icon("pencil", class_name="h-3.5 w-3.5"),
                                    on_click=lambda: (
                                        ConsultationsState.open_edit(r["id"])
                                    ),
                                    class_name="px-2 py-1.5 bg-blue-50 hover:bg-blue-100 text-blue-700 rounded-lg",
                                    title="Edit",
                                ),
                                rx.el.button(
                                    rx.icon(
                                        "trash-2", class_name="h-3.5 w-3.5"
                                    ),
                                    on_click=lambda: (
                                        ConsultationsState.confirm_delete(
                                            r["id"]
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
    )


def _pagination() -> rx.Component:
    return rx.el.div(
        rx.el.p(
            f"Showing page {ConsultationsState.page + 1} of {ConsultationsState.total_pages} • {ConsultationsState.total_count} records",
            class_name="text-xs text-gray-500",
        ),
        rx.el.div(
            secondary_btn(
                rx.icon("chevron-left", class_name="h-4 w-4"),
                "Prev",
                type="button",
                on_click=ConsultationsState.prev_page,
            ),
            secondary_btn(
                "Next",
                rx.icon("chevron-right", class_name="h-4 w-4"),
                type="button",
                on_click=ConsultationsState.next_page,
            ),
            class_name="flex gap-2",
        ),
        class_name="flex items-center justify-between px-4 py-3 border-t border-gray-200",
    )


def _form_modal() -> rx.Component:
    return modal(
        ConsultationsState.form_open,
        rx.cond(
            ConsultationsState.editing_id != 0,
            "Edit Consultation",
            "New Consultation",
        ).to(str),
        ConsultationsState.close_form,
        error_banner(ConsultationsState.form_error),
        rx.el.div(
            form_field(
                "Patient *",
                rx.el.select(
                    rx.foreach(
                        ConsultationsState.patients,
                        lambda p: rx.el.option(
                            p["label"], value=p["id"].to_string()
                        ),
                    ),
                    value=ConsultationsState.form_patient_id.to_string(),
                    on_change=ConsultationsState.set_form_patient,
                    class_name=SELECT_CLS,
                ),
            ),
            form_field(
                "Doctor *",
                rx.el.select(
                    rx.foreach(
                        ConsultationsState.doctors,
                        lambda d: rx.el.option(
                            d["label"], value=d["id"].to_string()
                        ),
                    ),
                    value=ConsultationsState.form_doctor_id.to_string(),
                    on_change=ConsultationsState.set_form_doctor,
                    class_name=SELECT_CLS,
                ),
            ),
            form_field(
                "Date *",
                rx.el.input(
                    type="date",
                    on_change=ConsultationsState.set_form_date,
                    class_name=INPUT_CLS,
                    default_value=ConsultationsState.form_date,
                ),
            ),
            class_name="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4",
        ),
        form_field(
            "Symptoms *",
            rx.el.textarea(
                rows="2",
                on_change=ConsultationsState.set_form_symptoms,
                class_name=INPUT_CLS,
                default_value=ConsultationsState.form_symptoms,
            ),
        ),
        rx.el.div(class_name="h-3"),
        form_field(
            "Diagnosis *",
            rx.el.textarea(
                rows="2",
                on_change=ConsultationsState.set_form_diagnosis,
                class_name=INPUT_CLS,
                default_value=ConsultationsState.form_diagnosis,
            ),
        ),
        rx.el.div(class_name="h-3"),
        form_field(
            "Treatment / Prescription",
            rx.el.textarea(
                rows="3",
                on_change=ConsultationsState.set_form_treatment,
                class_name=INPUT_CLS,
                default_value=ConsultationsState.form_treatment,
            ),
        ),
        rx.el.div(
            secondary_btn(
                rx.icon("rotate-ccw", class_name="h-4 w-4"),
                "Reset",
                type="button",
                on_click=ConsultationsState.reset_form,
            ),
            secondary_btn(
                "Cancel", type="button", on_click=ConsultationsState.close_form
            ),
            primary_btn(
                rx.icon("save", class_name="h-4 w-4"),
                "Save Consultation",
                type="button",
                on_click=ConsultationsState.save_consultation,
            ),
            class_name="flex justify-end gap-2 mt-5",
        ),
    )


def _view_modal() -> rx.Component:
    r = ConsultationsState.view_row
    return modal(
        ConsultationsState.view_open,
        "Consultation Details",
        ConsultationsState.close_view,
        rx.el.div(
            rx.el.div(
                rx.el.p("Patient", class_name="text-xs text-gray-500"),
                rx.el.p(
                    r["patient"],
                    class_name="text-sm font-semibold text-gray-900",
                ),
                class_name="p-3 bg-gray-50 rounded-lg",
            ),
            rx.el.div(
                rx.el.p("Doctor", class_name="text-xs text-gray-500"),
                rx.el.p(
                    r["doctor"],
                    class_name="text-sm font-semibold text-gray-900",
                ),
                class_name="p-3 bg-gray-50 rounded-lg",
            ),
            rx.el.div(
                rx.el.p("Date", class_name="text-xs text-gray-500"),
                rx.el.p(
                    r["date"], class_name="text-sm font-semibold text-gray-900"
                ),
                class_name="p-3 bg-gray-50 rounded-lg",
            ),
            rx.el.div(
                rx.el.p("Status", class_name="text-xs text-gray-500"),
                rx.el.p(
                    r["status"],
                    class_name="text-sm font-semibold text-gray-900",
                ),
                class_name="p-3 bg-gray-50 rounded-lg",
            ),
            class_name="grid grid-cols-2 gap-3 mb-4",
        ),
        rx.el.div(
            rx.el.p("Symptoms", class_name="text-xs text-gray-500 uppercase"),
            rx.el.p(r["symptoms"], class_name="text-sm text-gray-800 mt-1"),
            class_name="p-3 bg-gray-50 rounded-lg mb-3",
        ),
        rx.el.div(
            rx.el.p("Diagnosis", class_name="text-xs text-gray-500 uppercase"),
            rx.el.p(r["diagnosis"], class_name="text-sm text-gray-800 mt-1"),
            class_name="p-3 bg-gray-50 rounded-lg mb-3",
        ),
        rx.el.div(
            rx.el.p("Treatment", class_name="text-xs text-gray-500 uppercase"),
            rx.el.p(
                rx.cond(r["treatment"] != "", r["treatment"], "—"),
                class_name="text-sm text-gray-800 mt-1",
            ),
            class_name="p-3 bg-gray-50 rounded-lg",
        ),
        rx.el.div(
            secondary_btn(
                rx.icon("printer", class_name="h-4 w-4"),
                "Print",
                type="button",
                on_click=ConsultationsState.print_page,
            ),
            primary_btn(
                "Close", type="button", on_click=ConsultationsState.close_view
            ),
            class_name="flex justify-end gap-2 mt-5",
        ),
    )


def consultations_page() -> rx.Component:
    return page_shell(
        "Consultations",
        [("Home", "/dashboard"), ("Consultations", "/consultations")],
        loading_overlay(ConsultationsState.loading),
        rx.el.div(
            success_banner(ConsultationsState.success_message),
            class_name="",
        ),
        rx.el.div(
            _toolbar(),
            _table(),
            _pagination(),
            class_name="bg-white rounded-lg border border-gray-200 overflow-hidden",
        ),
        _form_modal(),
        _view_modal(),
        confirm_dialog(
            ConsultationsState.delete_open,
            "Delete Consultation?",
            "This action cannot be undone. Are you sure you want to delete this consultation?",
            ConsultationsState.delete_consultation,
            ConsultationsState.cancel_delete,
        ),
    )
