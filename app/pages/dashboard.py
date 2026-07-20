import reflex as rx
from app.components.charts import (
    lab_stats_chart,
    monthly_consultations_chart,
    patient_growth_chart,
    prescription_stats_chart,
)
from app.components.kpi_cards import kpi_cards
from app.components.layout import loading_overlay, page_shell
from app.components.sections import (
    history_summary_section,
    recent_consultations,
    recent_labs,
    recent_prescriptions,
    reports_search_section,
    system_status_section,
)
from app.states.dashboard_state import DashboardState


def dashboard_page() -> rx.Component:
    return page_shell(
        "Dashboard",
        [("Home", "/dashboard"), ("Dashboard", "/dashboard")],
        loading_overlay(DashboardState.loading),
        kpi_cards(),
        rx.el.div(
            monthly_consultations_chart(),
            patient_growth_chart(),
            class_name="grid grid-cols-1 lg:grid-cols-2 gap-6",
        ),
        rx.el.div(
            prescription_stats_chart(),
            lab_stats_chart(),
            class_name="grid grid-cols-1 lg:grid-cols-2 gap-6",
        ),
        rx.el.div(
            rx.el.div(
                recent_consultations(),
                recent_prescriptions(),
                recent_labs(),
                class_name="flex flex-col gap-6 lg:col-span-2",
            ),
            rx.el.div(
                system_status_section(),
                history_summary_section(),
                reports_search_section(),
                class_name="flex flex-col gap-6",
            ),
            class_name="grid grid-cols-1 lg:grid-cols-3 gap-6",
        ),
    )
