import reflex as rx
from app.states.dashboard_state import (
    DashboardState,
    HistorySummary,
    RecentConsultation,
    RecentLab,
    RecentPrescription,
)


def _status_badge(status: rx.Var) -> rx.Component:
    return rx.el.span(
        status,
        class_name=rx.match(
            status,
            (
                "Completed",
                "px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-700 w-fit",
            ),
            (
                "Active",
                "px-2 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-700 w-fit",
            ),
            (
                "Pending",
                "px-2 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-700 w-fit",
            ),
            (
                "In Progress",
                "px-2 py-0.5 rounded-full text-xs font-medium bg-orange-100 text-orange-700 w-fit",
            ),
            (
                "Follow-up",
                "px-2 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-700 w-fit",
            ),
            "px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-700 w-fit",
        ),
    )


def _card(title: str, icon: str, *children: rx.Component) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.icon(icon, class_name="h-5 w-5 text-blue-600"),
                rx.el.h3(
                    title, class_name="text-base font-semibold text-gray-900"
                ),
                class_name="flex items-center gap-2",
            ),
            class_name="px-5 py-4 border-b border-gray-200",
        ),
        rx.el.div(*children, class_name="p-0"),
        class_name="bg-white rounded-lg border border-gray-200 overflow-hidden",
    )


def _consult_row(c: RecentConsultation) -> rx.Component:
    return rx.el.tr(
        rx.el.td(
            c["patient"],
            class_name="px-4 py-3 text-sm text-gray-900 font-medium",
        ),
        rx.el.td(
            c["doctor"],
            class_name="px-4 py-3 text-sm text-gray-600 hidden md:table-cell",
        ),
        rx.el.td(
            c["diagnosis"],
            class_name="px-4 py-3 text-sm text-gray-600 hidden lg:table-cell",
        ),
        rx.el.td(c["date"], class_name="px-4 py-3 text-sm text-gray-500"),
        rx.el.td(_status_badge(c["status"]), class_name="px-4 py-3"),
        class_name="border-t border-gray-100 hover:bg-gray-50",
    )


def recent_consultations() -> rx.Component:
    return _card(
        "Recent Consultations",
        "stethoscope",
        rx.el.div(
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
                            "Diagnosis",
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
                    ),
                    class_name="bg-gray-50",
                ),
                rx.el.tbody(
                    rx.foreach(
                        DashboardState.recent_consultations, _consult_row
                    )
                ),
                class_name="table-auto w-full",
            ),
            class_name="overflow-x-auto",
        ),
    )


def _presc_row(p: RecentPrescription) -> rx.Component:
    return rx.el.tr(
        rx.el.td(
            p["patient"],
            class_name="px-4 py-3 text-sm text-gray-900 font-medium",
        ),
        rx.el.td(p["medication"], class_name="px-4 py-3 text-sm text-gray-600"),
        rx.el.td(
            p["dosage"],
            class_name="px-4 py-3 text-sm text-gray-600 hidden md:table-cell",
        ),
        rx.el.td(
            p["date"],
            class_name="px-4 py-3 text-sm text-gray-500 hidden sm:table-cell",
        ),
        rx.el.td(_status_badge(p["status"]), class_name="px-4 py-3"),
        class_name="border-t border-gray-100 hover:bg-gray-50",
    )


def recent_prescriptions() -> rx.Component:
    return _card(
        "Recent Prescriptions",
        "pill",
        rx.el.div(
            rx.el.table(
                rx.el.thead(
                    rx.el.tr(
                        rx.el.th(
                            "Patient",
                            class_name="px-4 py-2 text-left text-xs font-semibold text-gray-500 uppercase",
                        ),
                        rx.el.th(
                            "Medication",
                            class_name="px-4 py-2 text-left text-xs font-semibold text-gray-500 uppercase",
                        ),
                        rx.el.th(
                            "Dosage",
                            class_name="px-4 py-2 text-left text-xs font-semibold text-gray-500 uppercase hidden md:table-cell",
                        ),
                        rx.el.th(
                            "Date",
                            class_name="px-4 py-2 text-left text-xs font-semibold text-gray-500 uppercase hidden sm:table-cell",
                        ),
                        rx.el.th(
                            "Status",
                            class_name="px-4 py-2 text-left text-xs font-semibold text-gray-500 uppercase",
                        ),
                    ),
                    class_name="bg-gray-50",
                ),
                rx.el.tbody(
                    rx.foreach(DashboardState.recent_prescriptions, _presc_row)
                ),
                class_name="table-auto w-full",
            ),
            class_name="overflow-x-auto",
        ),
    )


def _lab_row(l: RecentLab) -> rx.Component:
    return rx.el.tr(
        rx.el.td(
            l["patient"],
            class_name="px-4 py-3 text-sm text-gray-900 font-medium",
        ),
        rx.el.td(l["test"], class_name="px-4 py-3 text-sm text-gray-600"),
        rx.el.td(
            l["result"],
            class_name="px-4 py-3 text-sm text-gray-600 hidden md:table-cell",
        ),
        rx.el.td(
            l["date"],
            class_name="px-4 py-3 text-sm text-gray-500 hidden sm:table-cell",
        ),
        rx.el.td(_status_badge(l["status"]), class_name="px-4 py-3"),
        class_name="border-t border-gray-100 hover:bg-gray-50",
    )


def recent_labs() -> rx.Component:
    return _card(
        "Recent Laboratory Reports",
        "test-tube",
        rx.el.div(
            rx.el.table(
                rx.el.thead(
                    rx.el.tr(
                        rx.el.th(
                            "Patient",
                            class_name="px-4 py-2 text-left text-xs font-semibold text-gray-500 uppercase",
                        ),
                        rx.el.th(
                            "Test",
                            class_name="px-4 py-2 text-left text-xs font-semibold text-gray-500 uppercase",
                        ),
                        rx.el.th(
                            "Result",
                            class_name="px-4 py-2 text-left text-xs font-semibold text-gray-500 uppercase hidden md:table-cell",
                        ),
                        rx.el.th(
                            "Date",
                            class_name="px-4 py-2 text-left text-xs font-semibold text-gray-500 uppercase hidden sm:table-cell",
                        ),
                        rx.el.th(
                            "Status",
                            class_name="px-4 py-2 text-left text-xs font-semibold text-gray-500 uppercase",
                        ),
                    ),
                    class_name="bg-gray-50",
                ),
                rx.el.tbody(rx.foreach(DashboardState.recent_labs, _lab_row)),
                class_name="table-auto w-full",
            ),
            class_name="overflow-x-auto",
        ),
    )


def _hist_row(h: HistorySummary) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon("activity", class_name="h-4 w-4 text-blue-600"),
            class_name="h-8 w-8 rounded-full bg-blue-100 flex items-center justify-center shrink-0",
        ),
        rx.el.div(
            rx.el.p(
                h["patient"], class_name="text-sm font-semibold text-gray-900"
            ),
            rx.el.p(h["condition"], class_name="text-xs text-gray-600"),
            rx.el.p(
                f"Since {h['onset']}", class_name="text-xs text-gray-400 mt-0.5"
            ),
            class_name="flex-1 min-w-0",
        ),
        class_name="flex items-start gap-3 px-5 py-3 border-t border-gray-100 first:border-t-0",
    )


def history_summary_section() -> rx.Component:
    return _card(
        "Patient Medical History Summary",
        "history",
        rx.foreach(DashboardState.history_summary, _hist_row),
    )


def _search_row(r: dict) -> rx.Component:
    return rx.el.div(
        rx.icon("user", class_name="h-4 w-4 text-blue-600"),
        rx.el.div(
            rx.el.p(
                r["title"], class_name="text-sm font-semibold text-gray-900"
            ),
            rx.el.p(r["subtitle"], class_name="text-xs text-gray-500"),
        ),
        class_name="flex items-center gap-3 px-4 py-3 border-t border-gray-100 first:border-t-0 hover:bg-gray-50",
    )


def reports_search_section() -> rx.Component:
    return _card(
        "Reports & Search",
        "search",
        rx.el.div(
            rx.el.div(
                rx.el.input(
                    placeholder="Search patients by name or MRN...",
                    default_value=DashboardState.search_query,
                    on_change=DashboardState.set_search_query.debounce(300),
                    class_name="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-hidden focus:ring-2 focus:ring-blue-500",
                ),
                rx.el.button(
                    rx.icon("search", class_name="h-4 w-4"),
                    "Search",
                    on_click=DashboardState.run_search,
                    class_name="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 flex items-center gap-2",
                ),
                class_name="flex gap-2 p-4",
            ),
            rx.cond(
                DashboardState.search_results.length() > 0,
                rx.el.div(
                    rx.foreach(DashboardState.search_results, _search_row)
                ),
                rx.el.p(
                    "Type a query and click Search to find patients.",
                    class_name="px-4 pb-4 text-xs text-gray-500",
                ),
            ),
        ),
    )


def system_status_section() -> rx.Component:
    def _row(label: str, value: rx.Var, dot_cls: str) -> rx.Component:
        return rx.el.div(
            rx.el.div(
                rx.el.span(class_name=f"h-2 w-2 rounded-full {dot_cls}"),
                rx.el.p(label, class_name="text-sm text-gray-700"),
                class_name="flex items-center gap-2",
            ),
            rx.el.p(value, class_name="text-sm font-medium text-gray-900"),
            class_name="flex items-center justify-between px-5 py-3 border-t border-gray-100 first:border-t-0",
        )

    return _card(
        "System Status",
        "activity",
        _row("Database", DashboardState.db_status, "bg-green-500"),
        _row("API Service", "Online", "bg-green-500"),
        _row("Report Engine", "Ready", "bg-green-500"),
        _row(
            "Doctors on Roster",
            DashboardState.total_doctors.to_string(),
            "bg-blue-500",
        ),
        _row("Last Refresh", DashboardState.last_updated, "bg-gray-400"),
    )
