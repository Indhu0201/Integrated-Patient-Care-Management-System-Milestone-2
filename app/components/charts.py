import reflex as rx
from app.states.dashboard_state import DashboardState

TOOLTIP_PROPS = {
    "content_style": {
        "background": "white",
        "borderColor": "#E5E7EB",
        "borderRadius": "0.5rem",
        "fontFamily": "Inter, sans-serif",
        "fontSize": "0.85rem",
        "padding": "0.5rem 0.75rem",
    },
    "label_style": {"color": "#111827", "fontWeight": "600"},
    "item_style": {"color": "#374151"},
    "separator": "",
}

CHART_CLS = "[&_.recharts-tooltip-item-value]:!text-gray-900 [&_.recharts-tooltip-item-name]:text-gray-600"


def _chart_card(title: str, subtitle: str, chart: rx.Component) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h3(title, class_name="text-base font-semibold text-gray-900"),
            rx.el.p(subtitle, class_name="text-xs text-gray-500 mt-0.5"),
            class_name="mb-4",
        ),
        chart,
        class_name="bg-white rounded-lg border border-gray-200 p-5",
    )


def monthly_consultations_chart() -> rx.Component:
    chart = rx.recharts.bar_chart(
        rx.recharts.cartesian_grid(
            horizontal=True, vertical=False, class_name="opacity-25"
        ),
        rx.recharts.graphing_tooltip(**TOOLTIP_PROPS),
        rx.recharts.bar(
            data_key="count",
            name="Consultations",
            fill="#2563EB",
            radius=[6, 6, 0, 0],
        ),
        rx.recharts.x_axis(
            data_key="month",
            axis_line=False,
            tick_line=False,
            custom_attrs={"fontSize": "12px"},
        ),
        rx.recharts.y_axis(
            axis_line=False, tick_line=False, custom_attrs={"fontSize": "12px"}
        ),
        data=DashboardState.monthly_consultations,
        width="100%",
        height=260,
        bar_size=32,
        margin={"left": 10, "right": 10, "top": 10},
        class_name=CHART_CLS,
    )
    return _chart_card(
        "Monthly Consultations", "Consultations over the last 6 months", chart
    )


def prescription_stats_chart() -> rx.Component:
    chart = rx.recharts.bar_chart(
        rx.recharts.cartesian_grid(
            horizontal=True, vertical=False, class_name="opacity-25"
        ),
        rx.recharts.graphing_tooltip(**TOOLTIP_PROPS),
        rx.recharts.bar(
            data_key="count",
            name="Prescriptions",
            fill="#7C3AED",
            radius=[6, 6, 0, 0],
        ),
        rx.recharts.x_axis(
            data_key="name",
            axis_line=False,
            tick_line=False,
            custom_attrs={"fontSize": "11px"},
            interval=0,
            angle=-15,
            text_anchor="end",
            height=50,
        ),
        rx.recharts.y_axis(
            axis_line=False, tick_line=False, custom_attrs={"fontSize": "12px"}
        ),
        data=DashboardState.prescription_stats,
        width="100%",
        height=260,
        bar_size=28,
        margin={"left": 10, "right": 10, "top": 10, "bottom": 10},
        class_name=CHART_CLS,
    )
    return _chart_card(
        "Prescription Statistics", "Top prescribed medications", chart
    )


def lab_stats_chart() -> rx.Component:
    chart = rx.recharts.bar_chart(
        rx.recharts.cartesian_grid(
            horizontal=True, vertical=False, class_name="opacity-25"
        ),
        rx.recharts.graphing_tooltip(**TOOLTIP_PROPS),
        rx.recharts.bar(
            data_key="count", name="Tests", fill="#EA580C", radius=[6, 6, 0, 0]
        ),
        rx.recharts.x_axis(
            data_key="name",
            axis_line=False,
            tick_line=False,
            custom_attrs={"fontSize": "11px"},
            interval=0,
            angle=-15,
            text_anchor="end",
            height=50,
        ),
        rx.recharts.y_axis(
            axis_line=False, tick_line=False, custom_attrs={"fontSize": "12px"}
        ),
        data=DashboardState.lab_stats,
        width="100%",
        height=260,
        bar_size=28,
        margin={"left": 10, "right": 10, "top": 10, "bottom": 10},
        class_name=CHART_CLS,
    )
    return _chart_card(
        "Laboratory Statistics", "Tests grouped by category", chart
    )


def patient_growth_chart() -> rx.Component:
    chart = rx.recharts.line_chart(
        rx.recharts.cartesian_grid(
            horizontal=True, vertical=False, class_name="opacity-25"
        ),
        rx.recharts.graphing_tooltip(**TOOLTIP_PROPS),
        rx.recharts.line(
            data_key="count",
            name="New Patients",
            stroke="#059669",
            stroke_width=2,
            type_="natural",
        ),
        rx.recharts.x_axis(
            data_key="month",
            axis_line=False,
            tick_line=False,
            custom_attrs={"fontSize": "12px"},
        ),
        rx.recharts.y_axis(
            axis_line=False, tick_line=False, custom_attrs={"fontSize": "12px"}
        ),
        data=DashboardState.patient_growth,
        width="100%",
        height=260,
        margin={"left": 10, "right": 10, "top": 10},
        class_name=CHART_CLS,
    )
    return _chart_card(
        "Patient Growth", "Newly registered patients per month", chart
    )
