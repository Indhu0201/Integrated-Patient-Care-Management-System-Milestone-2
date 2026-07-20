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
from app.states.laboratory_state import LaboratoryState


def _toolbar() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.input(
                placeholder="Search by patient, doctor, test...",
                default_value=LaboratoryState.search_query,
                on_change=LaboratoryState.set_search_query.debounce(300),
                class_name=INPUT_CLS + " min-w-72",
            ),
            secondary_btn(
                rx.icon("arrow-up-down", class_name="h-4 w-4"),
                rx.cond(LaboratoryState.sort_desc, "Newest", "Oldest"),
                type="button",
                on_click=LaboratoryState.toggle_sort,
            ),
            class_name="flex flex-wrap gap-2 items-center",
        ),
        primary_btn(
            rx.icon("plus", class_name="h-4 w-4"),
            "New Lab Report",
            type="button",
            on_click=LaboratoryState.open_new,
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
                        "Test Type",
                        class_name="px-4 py-2 text-left text-xs font-semibold text-gray-500 uppercase",
                    ),
                    rx.el.th(
                        "Result",
                        class_name="px-4 py-2 text-left text-xs font-semibold text-gray-500 uppercase hidden lg:table-cell",
                    ),
                    rx.el.th(
                        "Date",
                        class_name="px-4 py-2 text-left text-xs font-semibold text-gray-500 uppercase",
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
                    LaboratoryState.page_rows,
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
                            r["test_type"],
                            class_name="px-4 py-3 text-sm text-gray-800 font-medium",
                        ),
                        rx.el.td(
                            r["result"],
                            class_name="px-4 py-3 text-sm text-gray-600 hidden lg:table-cell",
                        ),
                        rx.el.td(
                            r["date"],
                            class_name="px-4 py-3 text-sm text-gray-600",
                        ),
                        rx.el.td(
                            rx.el.span(
                                r["status"],
                                class_name=rx.match(
                                    r["status"],
                                    (
                                        "Completed",
                                        "px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-700",
                                    ),
                                    (
                                        "Pending",
                                        "px-2 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-700",
                                    ),
                                    (
                                        "In Progress",
                                        "px-2 py-0.5 rounded-full text-xs font-medium bg-orange-100 text-orange-700",
                                    ),
                                    "px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-700",
                                ),
                            ),
                            class_name="px-4 py-3",
                        ),
                        rx.el.td(
                            rx.el.div(
                                rx.el.button(
                                    rx.icon("eye", class_name="h-3.5 w-3.5"),
                                    on_click=lambda: LaboratoryState.open_view(
                                        r["id"]
                                    ),
                                    class_name="px-2 py-1.5 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg",
                                    title="View",
                                ),
                                rx.el.button(
                                    rx.icon(
                                        "download", class_name="h-3.5 w-3.5"
                                    ),
                                    on_click=lambda: (
                                        LaboratoryState.download_pdf(r["id"])
                                    ),
                                    class_name="px-2 py-1.5 bg-emerald-50 hover:bg-emerald-100 text-emerald-700 rounded-lg",
                                    title="Download PDF",
                                ),
                                rx.el.button(
                                    rx.icon("pencil", class_name="h-3.5 w-3.5"),
                                    on_click=lambda: LaboratoryState.open_edit(
                                        r["id"]
                                    ),
                                    class_name="px-2 py-1.5 bg-blue-50 hover:bg-blue-100 text-blue-700 rounded-lg",
                                    title="Edit",
                                ),
                                rx.el.button(
                                    rx.icon(
                                        "trash-2", class_name="h-3.5 w-3.5"
                                    ),
                                    on_click=lambda: (
                                        LaboratoryState.confirm_delete(r["id"])
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
            f"Page {LaboratoryState.page + 1} of {LaboratoryState.total_pages} • {LaboratoryState.total_count} records",
            class_name="text-xs text-gray-500",
        ),
        rx.el.div(
            secondary_btn(
                rx.icon("chevron-left", class_name="h-4 w-4"),
                "Prev",
                type="button",
                on_click=LaboratoryState.prev_page,
            ),
            secondary_btn(
                "Next",
                rx.icon("chevron-right", class_name="h-4 w-4"),
                type="button",
                on_click=LaboratoryState.next_page,
            ),
            class_name="flex gap-2",
        ),
        class_name="flex items-center justify-between px-4 py-3 border-t border-gray-200",
    )


def _form_modal() -> rx.Component:
    return modal(
        LaboratoryState.form_open,
        rx.cond(
            LaboratoryState.editing_id != 0, "Edit Lab Report", "New Lab Report"
        ).to(str),
        LaboratoryState.close_form,
        error_banner(LaboratoryState.form_error),
        rx.el.div(
            form_field(
                "Patient *",
                rx.el.select(
                    rx.foreach(
                        LaboratoryState.patients,
                        lambda p: rx.el.option(
                            p["label"], value=p["id"].to_string()
                        ),
                    ),
                    value=LaboratoryState.form_patient_id.to_string(),
                    on_change=LaboratoryState.set_form_patient,
                    class_name=SELECT_CLS,
                ),
            ),
            form_field(
                "Doctor *",
                rx.el.select(
                    rx.foreach(
                        LaboratoryState.doctors,
                        lambda d: rx.el.option(
                            d["label"], value=d["id"].to_string()
                        ),
                    ),
                    value=LaboratoryState.form_doctor_id.to_string(),
                    on_change=LaboratoryState.set_form_doctor,
                    class_name=SELECT_CLS,
                ),
            ),
            class_name="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4",
        ),
        rx.el.div(
            form_field(
                "Test Type *",
                rx.el.select(
                    rx.foreach(
                        LaboratoryState.test_types,
                        lambda t: rx.el.option(t, value=t),
                    ),
                    value=LaboratoryState.form_test_type,
                    on_change=LaboratoryState.set_form_test_type,
                    class_name=SELECT_CLS,
                ),
            ),
            form_field(
                "Test Name (optional)",
                rx.el.input(
                    placeholder="Defaults to test type",
                    on_change=LaboratoryState.set_form_test_name,
                    class_name=INPUT_CLS,
                    default_value=LaboratoryState.form_test_name,
                ),
            ),
            form_field(
                "Test Date *",
                rx.el.input(
                    type="date",
                    on_change=LaboratoryState.set_form_date,
                    class_name=INPUT_CLS,
                    default_value=LaboratoryState.form_date,
                ),
            ),
            form_field(
                "Status",
                rx.el.select(
                    rx.foreach(
                        LaboratoryState.status_options,
                        lambda s: rx.el.option(s, value=s),
                    ),
                    value=LaboratoryState.form_status,
                    on_change=LaboratoryState.set_form_status,
                    class_name=SELECT_CLS,
                ),
            ),
            class_name="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4",
        ),
        form_field(
            "Result",
            rx.el.input(
                on_change=LaboratoryState.set_form_result,
                class_name=INPUT_CLS,
                default_value=LaboratoryState.form_result,
            ),
        ),
        rx.el.div(class_name="h-3"),
        form_field(
            "Remarks",
            rx.el.textarea(
                rows="3",
                on_change=LaboratoryState.set_form_remarks,
                class_name=INPUT_CLS,
                default_value=LaboratoryState.form_remarks,
            ),
        ),
        rx.el.div(class_name="h-3"),
        rx.el.div(
            rx.el.label(
                "Upload Report File",
                class_name="text-sm font-medium text-gray-700 mb-1 block",
            ),
            rx.upload.root(
                rx.el.div(
                    rx.icon("upload", class_name="h-4 w-4 text-blue-600"),
                    rx.el.p(
                        rx.cond(
                            LaboratoryState.form_upload_file != "",
                            LaboratoryState.form_upload_file,
                            "Drag & drop or click to upload",
                        ),
                        class_name="text-sm text-gray-600",
                    ),
                    class_name="flex items-center gap-2 justify-center",
                ),
                id="lab_upload",
                on_drop=LaboratoryState.handle_upload(
                    rx.upload_files(upload_id="lab_upload")
                ),
                multiple=False,
                class_name="border-2 border-dashed border-gray-300 rounded-lg p-4 cursor-pointer hover:border-blue-400 bg-gray-50",
            ),
        ),
        rx.el.div(
            secondary_btn(
                "Cancel", type="button", on_click=LaboratoryState.close_form
            ),
            primary_btn(
                rx.icon("save", class_name="h-4 w-4"),
                "Save Lab Report",
                type="button",
                on_click=LaboratoryState.save_lab,
            ),
            class_name="flex justify-end gap-2 mt-5",
        ),
    )


def _view_modal() -> rx.Component:
    r = LaboratoryState.view_row
    return modal(
        LaboratoryState.view_open,
        "Laboratory Report",
        LaboratoryState.close_view,
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
                rx.el.p("Test Type", class_name="text-xs text-gray-500"),
                rx.el.p(
                    r["test_type"],
                    class_name="text-sm font-semibold text-gray-900",
                ),
                class_name="p-3 bg-gray-50 rounded-lg",
            ),
            rx.el.div(
                rx.el.p("Test Date", class_name="text-xs text-gray-500"),
                rx.el.p(
                    r["date"], class_name="text-sm font-semibold text-gray-900"
                ),
                class_name="p-3 bg-gray-50 rounded-lg",
            ),
            rx.el.div(
                rx.el.p("Result", class_name="text-xs text-gray-500"),
                rx.el.p(
                    rx.cond(r["result"] != "", r["result"], "—"),
                    class_name="text-sm font-semibold text-gray-900",
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
            class_name="grid grid-cols-2 gap-3 mb-3",
        ),
        rx.el.div(
            rx.el.p("Remarks", class_name="text-xs text-gray-500 uppercase"),
            rx.el.p(
                rx.cond(r["remarks"] != "", r["remarks"], "—"),
                class_name="text-sm text-gray-800 mt-1",
            ),
            class_name="p-3 bg-gray-50 rounded-lg",
        ),
        rx.el.div(
            secondary_btn(
                rx.icon("printer", class_name="h-4 w-4"),
                "Print",
                type="button",
                on_click=LaboratoryState.print_page,
            ),
            secondary_btn(
                rx.icon("download", class_name="h-4 w-4"),
                "Download PDF",
                type="button",
                on_click=lambda: LaboratoryState.download_pdf(r["id"]),
            ),
            rx.cond(
                r["file_name"] != "",
                secondary_btn(
                    rx.icon("external-link", class_name="h-4 w-4"),
                    "View Uploaded",
                    type="button",
                    on_click=lambda: LaboratoryState.view_uploaded(r["id"]),
                ),
                rx.fragment(),
            ),
            primary_btn(
                "Close", type="button", on_click=LaboratoryState.close_view
            ),
            class_name="flex justify-end gap-2 mt-5 flex-wrap",
        ),
    )


def laboratory_page() -> rx.Component:
    return page_shell(
        "Laboratory",
        [("Home", "/dashboard"), ("Laboratory", "/laboratory")],
        loading_overlay(LaboratoryState.loading),
        success_banner(LaboratoryState.success_message),
        rx.el.div(
            _toolbar(),
            _table(),
            _pagination(),
            class_name="bg-white rounded-lg border border-gray-200 overflow-hidden",
        ),
        _form_modal(),
        _view_modal(),
        confirm_dialog(
            LaboratoryState.delete_open,
            "Delete Lab Report?",
            "This action cannot be undone. Are you sure you want to delete this lab report?",
            LaboratoryState.delete_lab,
            LaboratoryState.cancel_delete,
        ),
    )
