import reflex as rx
from app.database import SessionLocal, User, hash_password


class AuthState(rx.State):
    is_authenticated: bool = False
    admin_username: str = ""
    admin_full_name: str = ""
    login_error: str = ""
    login_loading: bool = False

    @rx.event
    def handle_login(self, form_data: dict):
        self.login_loading = True
        self.login_error = ""
        username = (form_data.get("username") or "").strip()
        password = form_data.get("password") or ""
        if not username or not password:
            self.login_error = "Please enter both username and password."
            self.login_loading = False
            return
        try:
            with SessionLocal() as db:
                user = (
                    db.query(User)
                    .filter(User.username == username, User.role == "admin")
                    .first()
                )
                if user is None or user.password_hash != hash_password(
                    password
                ):
                    self.login_error = "Invalid admin credentials."
                    self.login_loading = False
                    return
                self.is_authenticated = True
                self.admin_username = user.username
                self.admin_full_name = user.full_name
                self.login_loading = False
                return rx.redirect("/dashboard")
        except Exception as e:
            import logging

            logging.exception(f"Login error: {e}")
            self.login_error = "An error occurred during login."
            self.login_loading = False

    @rx.event
    def logout(self):
        self.is_authenticated = False
        self.admin_username = ""
        self.admin_full_name = ""
        return rx.redirect("/")

    @rx.event
    def require_auth(self):
        if not self.is_authenticated:
            return rx.redirect("/")
