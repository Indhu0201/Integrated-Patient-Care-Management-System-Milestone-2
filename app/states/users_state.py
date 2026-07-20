import logging
from typing import TypedDict

import reflex as rx

from app.database import SessionLocal, User, hash_password
from app.utils.validators import is_email, require


class AdminRow(TypedDict):
    id: int
    username: str
    full_name: str
    email: str
    is_active: bool
    created_at: str


class UsersState(rx.State):
    loading: bool = False
    rows: list[AdminRow] = []
    search_query: str = ""
    page: int = 0
    page_size: int = 10
    sort_desc: bool = True
    success_message: str = ""

    # Form
    form_open: bool = False
    editing_id: int = 0
    form_username: str = ""
    form_full_name: str = ""
    form_email: str = ""
    form_password: str = ""
    form_confirm: str = ""
    form_is_active: bool = True
    form_error: str = ""

    # Password modal
    pwd_open: bool = False
    pwd_user_id: int = 0
    pwd_current: str = ""
    pwd_new: str = ""
    pwd_confirm: str = ""
    pwd_error: str = ""

    # Delete
    delete_open: bool = False
    delete_id: int = 0

    @rx.var
    def total_count(self) -> int:
        return len(self._filtered())

    @rx.var
    def total_pages(self) -> int:
        return max(1, (self.total_count + self.page_size - 1) // self.page_size)

    @rx.var
    def page_rows(self) -> list[AdminRow]:
        data = self._filtered()
        start = self.page * self.page_size
        return data[start : start + self.page_size]

    def _filtered(self) -> list[AdminRow]:
        q = self.search_query.strip().lower()
        data = self.rows
        if q:
            data = [
                r
                for r in data
                if q in r["username"].lower()
                or q in r["full_name"].lower()
                or q in r["email"].lower()
            ]
        return sorted(
            data, key=lambda r: r["created_at"], reverse=self.sort_desc
        )

    @rx.event
    def load_page(self):
        return UsersState.load_rows

    @rx.event
    def load_rows(self):
        self.loading = True
        try:
            with SessionLocal() as db:
                admins = (
                    db.query(User)
                    .filter(User.role == "admin")
                    .order_by(User.created_at.desc())
                    .all()
                )
                self.rows = [
                    {
                        "id": u.id,
                        "username": u.username,
                        "full_name": u.full_name,
                        "email": u.email,
                        "is_active": bool(u.is_active),
                        "created_at": u.created_at.strftime("%Y-%m-%d")
                        if u.created_at
                        else "",
                    }
                    for u in admins
                ]
        except Exception as e:
            logging.exception(f"users load_rows: {e}")
        finally:
            self.loading = False

    @rx.event
    def set_search_query(self, v: str):
        self.search_query = v
        self.page = 0

    @rx.event
    def toggle_sort(self):
        self.sort_desc = not self.sort_desc

    @rx.event
    def next_page(self):
        if self.page + 1 < self.total_pages:
            self.page += 1

    @rx.event
    def prev_page(self):
        if self.page > 0:
            self.page -= 1

    # ---- Form ----
    def _reset_form(self):
        self.editing_id = 0
        self.form_username = ""
        self.form_full_name = ""
        self.form_email = ""
        self.form_password = ""
        self.form_confirm = ""
        self.form_is_active = True
        self.form_error = ""

    @rx.event
    def open_new(self):
        self._reset_form()
        self.form_open = True

    @rx.event
    def open_edit(self, user_id: int):
        row = next((r for r in self.rows if r["id"] == user_id), None)
        if row is None:
            return
        self.editing_id = user_id
        self.form_username = row["username"]
        self.form_full_name = row["full_name"]
        self.form_email = row["email"]
        self.form_password = ""
        self.form_confirm = ""
        self.form_is_active = row["is_active"]
        self.form_error = ""
        self.form_open = True

    @rx.event
    def close_form(self):
        self.form_open = False

    @rx.event
    def set_form_username(self, v: str):
        self.form_username = v

    @rx.event
    def set_form_full_name(self, v: str):
        self.form_full_name = v

    @rx.event
    def set_form_email(self, v: str):
        self.form_email = v

    @rx.event
    def set_form_password(self, v: str):
        self.form_password = v

    @rx.event
    def set_form_confirm(self, v: str):
        self.form_confirm = v

    @rx.event
    def toggle_form_active(self, value: bool):
        self.form_is_active = bool(value)

    def _validate_form(self) -> str:
        if not require(self.form_username):
            return "Username is required."
        if len(self.form_username.strip()) < 3:
            return "Username must be at least 3 characters."
        if not require(self.form_full_name):
            return "Full name is required."
        if not is_email(self.form_email):
            return "Please enter a valid email address."
        if not self.editing_id:
            if not require(self.form_password):
                return "Password is required for new users."
            if len(self.form_password) < 6:
                return "Password must be at least 6 characters."
            if self.form_password != self.form_confirm:
                return "Password and confirmation do not match."
        else:
            if self.form_password and self.form_password != self.form_confirm:
                return "Password and confirmation do not match."
        return ""

    @rx.event
    def save_user(self):
        err = self._validate_form()
        if err:
            self.form_error = err
            return
        try:
            with SessionLocal() as db:
                username = self.form_username.strip()
                email = self.form_email.strip()
                # Duplicate checks
                dup_username = (
                    db.query(User).filter(User.username == username).first()
                )
                if dup_username and dup_username.id != self.editing_id:
                    self.form_error = "Username already exists."
                    return
                dup_email = db.query(User).filter(User.email == email).first()
                if dup_email and dup_email.id != self.editing_id:
                    self.form_error = "Email already in use."
                    return

                if self.editing_id:
                    u = db.get(User, self.editing_id)
                    if u is None:
                        self.form_error = "User not found."
                        return
                else:
                    u = User(role="admin")
                    db.add(u)
                u.username = username
                u.email = email
                u.full_name = self.form_full_name.strip()
                u.role = "admin"
                u.is_active = self.form_is_active
                if self.form_password:
                    u.password_hash = hash_password(self.form_password)
                db.commit()
            self.form_open = False
            self.success_message = "User saved successfully."
            yield rx.toast.success("User saved.")
            yield UsersState.load_rows
        except Exception as e:
            logging.exception(f"save_user: {e}")
            self.form_error = "Failed to save user."

    # ---- Delete ----
    @rx.event
    def confirm_delete(self, user_id: int):
        self.delete_id = user_id
        self.delete_open = True

    @rx.event
    def cancel_delete(self):
        self.delete_open = False
        self.delete_id = 0

    @rx.event
    def delete_user(self):
        if not self.delete_id:
            return
        try:
            with SessionLocal() as db:
                admin_count = (
                    db.query(User).filter(User.role == "admin").count()
                )
                if admin_count <= 1:
                    yield rx.toast.error(
                        "Cannot delete the last remaining admin."
                    )
                    self.delete_open = False
                    self.delete_id = 0
                    return
                u = db.get(User, self.delete_id)
                if u is not None:
                    db.delete(u)
                    db.commit()
            self.delete_open = False
            self.delete_id = 0
            yield rx.toast.success("User deleted.")
            yield UsersState.load_rows
        except Exception as e:
            logging.exception(f"delete_user: {e}")
            yield rx.toast.error("Failed to delete user.")

    # ---- Password change ----
    @rx.event
    def open_change_password(self, user_id: int):
        self.pwd_user_id = user_id
        self.pwd_current = ""
        self.pwd_new = ""
        self.pwd_confirm = ""
        self.pwd_error = ""
        self.pwd_open = True

    @rx.event
    def close_change_password(self):
        self.pwd_open = False

    @rx.event
    def set_pwd_current(self, v: str):
        self.pwd_current = v

    @rx.event
    def set_pwd_new(self, v: str):
        self.pwd_new = v

    @rx.event
    def set_pwd_confirm(self, v: str):
        self.pwd_confirm = v

    @rx.event
    def save_password(self):
        if not self.pwd_current:
            self.pwd_error = "Current password is required."
            return
        if len(self.pwd_new) < 6:
            self.pwd_error = "New password must be at least 6 characters."
            return
        if self.pwd_new != self.pwd_confirm:
            self.pwd_error = "New password and confirmation do not match."
            return
        try:
            with SessionLocal() as db:
                u = db.get(User, self.pwd_user_id)
                if u is None:
                    self.pwd_error = "User not found."
                    return
                if u.password_hash != hash_password(self.pwd_current):
                    self.pwd_error = "Current password is incorrect."
                    return
                u.password_hash = hash_password(self.pwd_new)
                db.commit()
            self.pwd_open = False
            yield rx.toast.success("Password changed successfully.")
        except Exception as e:
            logging.exception(f"save_password: {e}")
            self.pwd_error = "Failed to update password."
