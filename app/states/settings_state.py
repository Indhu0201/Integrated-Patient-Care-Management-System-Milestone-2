import logging
import random
import string

import reflex as rx

from app.database import ReportLog, SessionLocal, Setting
from app.utils.validators import is_email, is_phone, require


DEFAULT_SETTINGS: dict[str, str] = {
    "hospital_name": "St. Mary's Integrated Care",
    "hospital_address": "123 Wellness Blvd, Springfield",
    "contact_email": "contact@ipcms.local",
    "contact_phone": "+1-555-0100",
    "timezone": "UTC",
    "theme": "light",
    "hospital_logo": "",
}

THEME_OPTIONS = ["light", "dark", "system"]
TIMEZONE_OPTIONS = [
    "UTC",
    "America/New_York",
    "America/Chicago",
    "America/Los_Angeles",
    "Europe/London",
    "Europe/Paris",
    "Asia/Tokyo",
    "Asia/Singapore",
    "Asia/Kolkata",
]


class SettingsState(rx.State):
    loading: bool = False
    hospital_name: str = ""
    hospital_address: str = ""
    contact_email: str = ""
    contact_phone: str = ""
    timezone: str = "UTC"
    theme: str = "light"
    hospital_logo: str = ""

    theme_options: list[str] = THEME_OPTIONS
    timezone_options: list[str] = TIMEZONE_OPTIONS

    form_error: str = ""
    success_message: str = ""

    total_reports: int = 0

    @rx.event
    def load_page(self):
        self.loading = True
        try:
            with SessionLocal() as db:
                rows = db.query(Setting).all()
                data = {r.key: r.value for r in rows}
                for k, v in DEFAULT_SETTINGS.items():
                    if k not in data:
                        db.add(Setting(key=k, value=v))
                        data[k] = v
                db.commit()
                self.hospital_name = data.get(
                    "hospital_name", DEFAULT_SETTINGS["hospital_name"]
                )
                self.hospital_address = data.get(
                    "hospital_address", DEFAULT_SETTINGS["hospital_address"]
                )
                self.contact_email = data.get(
                    "contact_email", DEFAULT_SETTINGS["contact_email"]
                )
                self.contact_phone = data.get(
                    "contact_phone", DEFAULT_SETTINGS["contact_phone"]
                )
                self.timezone = data.get("timezone", "UTC")
                self.theme = data.get("theme", "light")
                self.hospital_logo = data.get("hospital_logo", "")
                self.total_reports = db.query(ReportLog).count()
        except Exception as e:
            logging.exception(f"settings load: {e}")
        finally:
            self.loading = False

    @rx.event
    def set_hospital_name(self, v: str):
        self.hospital_name = v

    @rx.event
    def set_hospital_address(self, v: str):
        self.hospital_address = v

    @rx.event
    def set_contact_email(self, v: str):
        self.contact_email = v

    @rx.event
    def set_contact_phone(self, v: str):
        self.contact_phone = v

    @rx.event
    def set_timezone(self, v: str):
        self.timezone = v

    @rx.event
    def set_theme(self, v: str):
        self.theme = v

    def _validate(self) -> str:
        if not require(self.hospital_name):
            return "Hospital name is required."
        if not require(self.hospital_address):
            return "Hospital address is required."
        if not is_email(self.contact_email):
            return "Please enter a valid contact email."
        if not is_phone(self.contact_phone):
            return "Please enter a valid contact phone number."
        if self.theme not in THEME_OPTIONS:
            return "Invalid theme selection."
        return ""

    @rx.event
    def save_settings(self):
        err = self._validate()
        if err:
            self.form_error = err
            return
        self.form_error = ""
        try:
            payload = {
                "hospital_name": self.hospital_name.strip(),
                "hospital_address": self.hospital_address.strip(),
                "contact_email": self.contact_email.strip(),
                "contact_phone": self.contact_phone.strip(),
                "timezone": self.timezone,
                "theme": self.theme,
                "hospital_logo": self.hospital_logo,
            }
            with SessionLocal() as db:
                for k, v in payload.items():
                    row = db.query(Setting).filter(Setting.key == k).first()
                    if row is None:
                        db.add(Setting(key=k, value=v))
                    else:
                        row.value = v
                db.commit()
            self.success_message = "Settings saved successfully."
            yield rx.toast.success("Settings saved.")
        except Exception as e:
            logging.exception(f"save_settings: {e}")
            self.form_error = "Failed to save settings."

    @rx.event
    async def handle_logo_upload(self, files: list[rx.UploadFile]):
        if not files:
            return
        try:
            file = files[0]
            data = await file.read()
            upload_dir = rx.get_upload_dir()
            upload_dir.mkdir(parents=True, exist_ok=True)
            suffix = "".join(
                random.choices(string.ascii_lowercase + string.digits, k=8)
            )
            safe_name = f"logo_{suffix}_{file.name}"
            (upload_dir / safe_name).write_bytes(data)
            self.hospital_logo = safe_name
            yield rx.toast.success("Logo uploaded. Remember to save settings.")
        except Exception as e:
            logging.exception(f"handle_logo_upload: {e}")
            yield rx.toast.error("Logo upload failed.")

    @rx.event
    def clear_logo(self):
        self.hospital_logo = ""
