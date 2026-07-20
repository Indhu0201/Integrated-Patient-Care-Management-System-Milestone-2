import reflex as rx
from app.states.auth_state import AuthState

MENU: list[tuple[str, str, str]] = [
    ("Dashboard", "layout-dashboard", "/dashboard"),
    ("Electronic Health Records", "clipboard-list", "/ehr"),
    ("Consultations", "stethoscope", "/consultations"),
    ("Prescriptions", "pill", "/prescriptions"),
    ("Laboratory", "test-tube", "/laboratory"),
    ("Medical History", "history", "/medical-history"),
    ("Reports & Search", "search", "/reports"),
    ("Users", "users", "/users"),
    ("Settings", "settings", "/settings"),
]


def _nav_item(label: str, icon: str, href: str) -> rx.Component:
    return rx.el.a(
        rx.icon(icon, class_name="h-5 w-5 shrink-0"),
        rx.el.span(label, class_name="text-sm font-medium truncate"),
        href=href,
        class_name="flex items-center gap-3 px-4 py-2.5 rounded-lg text-blue-100 hover:bg-blue-700/60 hover:text-white transition-colors",
    )


def sidebar() -> rx.Component:
    return rx.el.aside(
        rx.el.div(
            rx.el.div(
                rx.icon("heart-pulse", class_name="h-7 w-7 text-white"),
                rx.el.div(
                    rx.el.p(
                        "IPCMS",
                        class_name="text-white font-bold text-lg leading-tight",
                    ),
                    rx.el.p("Admin Portal", class_name="text-blue-200 text-xs"),
                ),
                class_name="flex items-center gap-3 px-6 py-5 border-b border-blue-700/50",
            ),
            rx.el.nav(
                *[_nav_item(l, i, h) for l, i, h in MENU],
                class_name="flex flex-col gap-1 p-3 flex-1 overflow-y-auto",
            ),
            rx.el.div(
                rx.el.button(
                    rx.icon("log-out", class_name="h-5 w-5"),
                    rx.el.span("Logout", class_name="text-sm font-medium"),
                    on_click=AuthState.logout,
                    class_name="w-full flex items-center gap-3 px-4 py-2.5 rounded-lg text-blue-100 hover:bg-red-500/80 hover:text-white transition-colors",
                ),
                class_name="p-3 border-t border-blue-700/50",
            ),
            class_name="flex flex-col h-screen sticky top-0",
        ),
        class_name="bg-blue-800 w-64 shrink-0 hidden md:block",
    )
