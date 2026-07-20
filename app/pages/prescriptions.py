import reflex as rx

from app.components.layout import loading_overlay, page_shell
from app.components.modal import (
    INPUT_CLS,
    SELECT_CLS,
    confirm_dialog,
    error_banner,
    form_field,
    modal,
    primary_btn,
    secondary_btn,
    success_banner,
)
from app.states.prescriptions_state import PrescriptionsState


def _toolbar() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.input(
                placeholder="Search by patient, doctor, medication...",
                default_value=PrescriptionsState.search_query,
                on_change=PrescriptionsState.set_search_query.debounce(300),
                class_name=INPUT_CLS + " min-w-72",
            ),
            secondary_btn(
                rx.icon("arrow-up-down", class_name="h-4 w-4"),
                rx.cond(PrescriptionsState.sort_desc, "Newest", "Oldest"),
                type="button",
                on_click=PrescriptionsState.toggle_sort,
            ),
            class_name="flex flex-wrap gap-2 items-center",
        ),
        primary_btn(
            rx.icon("plus", class_name="h-4 w-4"),
            "New Prescription",
            type="button",
            on_click=PrescriptionsState.open_new,
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
                        "Medication",
                        class_name="px-4 py-2 text-left text-xs font-semibold text-gray-500 uppercase",
                    ),
                    rx.el.th(
                        "Dosage",
                        class_name="px-4 py-2 text-left text-xs font-semibold text-gray-500 uppercase hidden lg:table-cell",
                    ),
                    rx.el.th(
                        "Date",
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
                    PrescriptionsState.page_rows,
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
                            r["medication"],
                            class_name="px-4 py-3 text-sm text-gray-800 font-medium",
                        ),
                        rx.el.td(
                            r["dosage"],
                            class_name="px-4 py-3 text-sm text-gray-600 hidden lg:table-cell",
                        ),
                        rx.el.td(
                            r["date"],
                            class_name="px-4 py-3 text-sm text-gray-600",
                        ),
                        rx.el.td(
                            rx.el.div(
                                rx.el.button(
                                    rx.icon("eye", class_name="h-3.5 w-3.5"),
                                    on_click=lambda: (
                                        PrescriptionsState.open_view(r["id"])
                                    ),
                                    class_name="px-2 py-1.5 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg",
                                    title="View",
                                ),
                                rx.el.button(
                                    rx.icon(
                                        "download", class_name="h-3.5 w-3.5"
                                    ),
                                    on_click=lambda: (
                                        PrescriptionsState.download_pdf(r["id"])
                                    ),
                                    class_name="px-2 py-1.5 bg-emerald-50 hover:bg-emerald-100 text-emerald-700 rounded-lg",
                                    title="Download PDF",
                                ),
                                rx.el.button(
                                    rx.icon("pencil", class_name="h-3.5 w-3.5"),
                                    on_click=lambda: (
                                        PrescriptionsState.open_edit(r["id"])
                                    ),
                                    class_name="px-2 py-1.5 bg-blue-50 hover:bg-blue-100 text-blue-700 rounded-lg",
                                    title="Edit",
                                ),
                                rx.el.button(
                                    rx.icon(
                                        "trash-2", class_name="h-3.5 w-3.5"
                                    ),
                                    on_click=lambda: (
                                        PrescriptionsState.confirm_delete(
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
            f"Page {PrescriptionsState.page + 1} of {PrescriptionsState.total_pages} • {PrescriptionsState.total_count} records",
            class_name="text-xs text-gray-500",
        ),
        rx.el.div(
            secondary_btn(
                rx.icon("chevron-left", class_name="h-4 w-4"),
                "Prev",
                type="button",
                on_click=PrescriptionsState.prev_page,
            ),
            secondary_btn(
                "Next",
                rx.icon("chevron-right", class_name="h-4 w-4"),
                type="button",
                on_click=PrescriptionsState.next_page,
            ),
            class_name="flex gap-2",
        ),
        class_name="flex items-center justify-between px-4 py-3 border-t border-gray-200",
    )


def _form_modal() -> rx.Component:
    return modal(
        PrescriptionsState.form_open,
        rx.cond(
            PrescriptionsState.editing_id != 0,
            "Edit Prescription",
            "New Prescription",
        ).to(str),
        PrescriptionsState.close_form,
        error_banner(PrescriptionsState.form_error),
        rx.el.div(
            form_field(
                "Patient *",
                rx.el.select(
                    rx.foreach(
                        PrescriptionsState.patients,
                        lambda p: rx.el.option(
                            p["label"], value=p["id"].to_string()
                        ),
                    ),
                    value=PrescriptionsState.form_patient_id.to_string(),
                    on_change=PrescriptionsState.set_form_patient,
                    class_name=SELECT_CLS,
                ),
            ),
            form_field(
                "Doctor *",
                rx.el.select(
                    rx.foreach(
                        PrescriptionsState.doctors,
                        lambda d: rx.el.option(
                            d["label"], value=d["id"].to_string()
                        ),
                    ),
                    value=PrescriptionsState.form_doctor_id.to_string(),
                    on_change=PrescriptionsState.set_form_doctor,
                    class_name=SELECT_CLS,
                ),
            ),
            form_field(
                "Date *",
                rx.el.input(
                    type="date",
                    on_change=PrescriptionsState.set_form_date,
                    class_name=INPUT_CLS,
                    default_value=PrescriptionsState.form_date,
                ),
            ),
            class_name="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4",
        ),
        rx.el.div(
            form_field(
                "Medicine *",
                rx.el.input(
                    on_change=PrescriptionsState.set_form_medication,
                    class_name=INPUT_CLS,
                    default_value=PrescriptionsState.form_medication,
                ),
            ),
            form_field(
                "Dosage *",
                rx.el.input(
                    placeholder="e.g. 500mg",
                    on_change=PrescriptionsState.set_form_dosage,
                    class_name=INPUT_CLS,
                    default_value=PrescriptionsState.form_dosage,
                ),
            ),
            form_field(
                "Frequency *",
                rx.el.select(
                    rx.foreach(
                        PrescriptionsState.frequencies,
                        lambda f: rx.el.option(f, value=f),
                    ),
                    value=PrescriptionsState.form_frequency,
                    on_change=PrescriptionsState.set_form_frequency,
                    class_name=SELECT_CLS,
                ),
            ),
            form_field(
                "Duration *",
                rx.el.input(
                    placeholder="e.g. 7 days",
                    on_change=PrescriptionsState.set_form_duration,
                    class_name=INPUT_CLS,
                    default_value=PrescriptionsState.form_duration,
                ),
            ),
            class_name="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4",
        ),
        form_field(
            "Instructions",
            rx.el.textarea(
                rows="3",
                on_change=PrescriptionsState.set_form_instructions,
                class_name=INPUT_CLS,
                default_value=PrescriptionsState.form_instructions,
            ),
        ),
        rx.el.div(
            secondary_btn(
                "Cancel", type="button", on_click=PrescriptionsState.close_form
            ),
            primary_btn(
                rx.icon("save", class_name="h-4 w-4"),
                "Save Prescription",
                type="button",
                on_click=PrescriptionsState.save_prescription,
            ),
            class_name="flex justify-end gap-2 mt-5",
        ),
    )


def _view_modal() -> rx.Component:
    r = PrescriptionsState.view_row
    return modal(
        PrescriptionsState.view_open,
        "Prescription Details",
        PrescriptionsState.close_view,
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
            rx.el.div(
                rx.el.p("Medication", class_name="text-xs text-gray-500"),
                rx.el.p(
                    r["medication"],
                    class_name="text-sm font-semibold text-gray-900",
                ),
                class_name="p-3 bg-gray-50 rounded-lg",
            ),
            rx.el.div(
                rx.el.p("Dosage", class_name="text-xs text-gray-500"),
                rx.el.p(
                    r["dosage"],
                    class_name="text-sm font-semibold text-gray-900",
                ),
                class_name="p-3 bg-gray-50 rounded-lg",
            ),
            rx.el.div(
                rx.el.p("Frequency", class_name="text-xs text-gray-500"),
                rx.el.p(
                    r["frequency"],
                    class_name="text-sm font-semibold text-gray-900",
                ),
                class_name="p-3 bg-gray-50 rounded-lg",
            ),
            rx.el.div(
                rx.el.p("Duration", class_name="text-xs text-gray-500"),
                rx.el.p(
                    r["duration"],
                    class_name="text-sm font-semibold text-gray-900",
                ),
                class_name="p-3 bg-gray-50 rounded-lg",
            ),
            class_name="grid grid-cols-2 gap-3 mb-3",
        ),
        rx.el.div(
            rx.el.p(
                "Instructions", class_name="text-xs text-gray-500 uppercase"
            ),
            rx.el.p(
                rx.cond(r["instructions"] != "", r["instructions"], "—"),
                class_name="text-sm text-gray-800 mt-1",
            ),
            class_name="p-3 bg-gray-50 rounded-lg",
        ),
        rx.el.div(
            secondary_btn(
                rx.icon("printer", class_name="h-4 w-4"),
                "Print",
                type="button",
                on_click=PrescriptionsState.print_page,
            ),
            secondary_btn(
                rx.icon("download", class_name="h-4 w-4"),
                "Download PDF",
                type="button",
                on_click=lambda: PrescriptionsState.download_pdf(r["id"]),
            ),
            primary_btn(
                "Close", type="button", on_click=PrescriptionsState.close_view
            ),
            class_name="flex justify-end gap-2 mt-5",
        ),
    )


def prescriptions_page() -> rx.Component:
    return page_shell(
        "Prescriptions",
        [("Home", "/dashboard"), ("Prescriptions", "/prescriptions")],
        loading_overlay(PrescriptionsState.loading),
        success_banner(PrescriptionsState.success_message),
        rx.el.div(
            _toolbar(),
            _table(),
            _pagination(),
            class_name="bg-white rounded-lg border border-gray-200 overflow-hidden",
        ),
        _form_modal(),
        _view_modal(),
        confirm_dialog(
            PrescriptionsState.delete_open,
            "Delete Prescription?",
            "This action cannot be undone. Are you sure you want to delete this prescription?",
            PrescriptionsState.delete_prescription,
            PrescriptionsState.cancel_delete,
        ),
    )
