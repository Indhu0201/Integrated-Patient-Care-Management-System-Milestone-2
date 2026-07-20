import reflex as rx
from app.states.dashboard_state import DashboardState


def _kpi_card(
    label: str, value: rx.Var, icon: str, color: str, accent: str
) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.icon(icon, class_name=f"h-6 w-6 {color}"),
                class_name=f"h-12 w-12 rounded-lg {accent} flex items-center justify-center",
            ),
            rx.el.div(
                rx.el.p(label, class_name="text-sm font-medium text-gray-500"),
                rx.el.p(
                    value.to_string(),
                    class_name="text-2xl font-bold text-gray-900",
                ),
                class_name="flex flex-col",
            ),
            class_name="flex items-center gap-4",
        ),
        class_name="bg-white rounded-lg border border-gray-200 p-5 hover:shadow-md transition-shadow",
    )


def kpi_cards() -> rx.Component:
    return rx.el.div(
        _kpi_card(
            "Total Patients",
            DashboardState.total_patients,
            "users",
            "text-blue-600",
            "bg-blue-100",
        ),
        _kpi_card(
            "Total Consultations",
            DashboardState.total_consultations,
            "stethoscope",
            "text-emerald-600",
            "bg-emerald-100",
        ),
        _kpi_card(
            "Total Prescriptions",
            DashboardState.total_prescriptions,
            "pill",
            "text-purple-600",
            "bg-purple-100",
        ),
        _kpi_card(
            "Total Lab Tests",
            DashboardState.total_lab_tests,
            "test-tube",
            "text-orange-600",
            "bg-orange-100",
        ),
        _kpi_card(
            "Reports Generated",
            DashboardState.total_reports,
            "file-text",
            "text-rose-600",
            "bg-rose-100",
        ),
        class_name="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4",
    )
