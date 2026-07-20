import reflex as rx

from app.database import init_db
from app.pages.consultations import consultations_page
from app.pages.dashboard import dashboard_page
from app.pages.ehr import ehr_page
from app.pages.errors import not_found_page, server_error_page
from app.pages.laboratory import laboratory_page
from app.pages.login import login_page
from app.pages.medical_history import medical_history_page
from app.pages.prescriptions import prescriptions_page
from app.pages.reports import reports_page
from app.pages.settings import settings_page
from app.pages.users import users_page
from app.states.auth_state import AuthState
from app.states.consultations_state import ConsultationsState
from app.states.dashboard_state import DashboardState
from app.states.ehr_state import EHRState
from app.states.laboratory_state import LaboratoryState
from app.states.medical_history_state import MedicalHistoryState
from app.states.prescriptions_state import PrescriptionsState
from app.states.reports_state import ReportsState
from app.states.settings_state import SettingsState
from app.states.users_state import UsersState

# Ensure database is initialized and seeded.
init_db()


def index() -> rx.Component:
    return login_page()


def dashboard() -> rx.Component:
    return dashboard_page()


def page_404() -> rx.Component:
    return not_found_page()


def page_500() -> rx.Component:
    return server_error_page()


app = rx.App(
    theme=rx.theme(appearance="light"),
    head_components=[
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(
            rel="preconnect", href="https://fonts.gstatic.com", cross_origin=""
        ),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap",
            rel="stylesheet",
        ),
    ],
    style={
        "font_family": "Inter, sans-serif",
    },
)

app.add_page(index, route="/", title="Admin Login | IPCMS")
app.add_page(
    dashboard,
    route="/dashboard",
    title="Dashboard | IPCMS",
    on_load=[AuthState.require_auth, DashboardState.load_dashboard],
)
app.add_page(
    ehr_page,
    route="/ehr",
    title="EHR | IPCMS",
    on_load=[AuthState.require_auth, EHRState.load_page],
)
app.add_page(
    consultations_page,
    route="/consultations",
    title="Consultations | IPCMS",
    on_load=[AuthState.require_auth, ConsultationsState.load_page],
)
app.add_page(
    prescriptions_page,
    route="/prescriptions",
    title="Prescriptions | IPCMS",
    on_load=[AuthState.require_auth, PrescriptionsState.load_page],
)
app.add_page(
    laboratory_page,
    route="/laboratory",
    title="Laboratory | IPCMS",
    on_load=[AuthState.require_auth, LaboratoryState.load_page],
)
app.add_page(
    medical_history_page,
    route="/medical-history",
    title="Medical History | IPCMS",
    on_load=[AuthState.require_auth, MedicalHistoryState.load_page],
)
app.add_page(
    reports_page,
    route="/reports",
    title="Reports & Search | IPCMS",
    on_load=[AuthState.require_auth, ReportsState.load_page],
)
app.add_page(
    users_page,
    route="/users",
    title="Users | IPCMS",
    on_load=[AuthState.require_auth, UsersState.load_page],
)
app.add_page(
    settings_page,
    route="/settings",
    title="Settings | IPCMS",
    on_load=[AuthState.require_auth, SettingsState.load_page],
)
app.add_page(page_404, route="/[[...splat]]", title="Not Found | IPCMS")
app.add_page(page_404, route="/404", title="Not Found | IPCMS")
app.add_page(page_500, route="/500", title="Server Error | IPCMS")
