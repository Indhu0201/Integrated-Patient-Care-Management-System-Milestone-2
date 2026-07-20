import reflex as rx

from app.components.layout import loading_overlay, page_shell
from app.components.modal import (
    INPUT_CLS,
    confirm_dialog,
    error_banner,
    form_field,
    modal,
    primary_btn,
    secondary_btn,
    success_banner,
)
from app.states.users_state import UsersState


def _toolbar() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.input(
                placeholder="Search by username, name, or email...",
                default_value=UsersState.search_query,
                on_change=UsersState.set_search_query.debounce(300),
                class_name=INPUT_CLS + " min-w-72",
            ),
            secondary_btn(
                rx.icon("arrow-up-down", class_name="h-4 w-4"),
                rx.cond(UsersState.sort_desc, "Newest", "Oldest"),
                type="button",
                on_click=UsersState.toggle_sort,
            ),
            class_name="flex flex-wrap gap-2 items-center",
        ),
        primary_btn(
            rx.icon("user-plus", class_name="h-4 w-4"),
            "Add User",
            type="button",
            on_click=UsersState.open_new,
        ),
        class_name="flex flex-wrap items-center justify-between gap-3 p-4 border-b border-gray-200",
    )


def _table() -> rx.Component:
    return rx.el.div(
        rx.el.table(
            rx.el.thead(
                rx.el.tr(
                    rx.el.th(
                        "Username",
                        class_name="px-4 py-2 text-left text-xs font-semibold text-gray-500 uppercase",
                    ),
                    rx.el.th(
                        "Full Name",
                        class_name="px-4 py-2 text-left text-xs font-semibold text-gray-500 uppercase",
                    ),
                    rx.el.th(
                        "Email",
                        class_name="px-4 py-2 text-left text-xs font-semibold text-gray-500 uppercase hidden md:table-cell",
                    ),
                    rx.el.th(
                        "Status",
                        class_name="px-4 py-2 text-left text-xs font-semibold text-gray-500 uppercase",
                    ),
                    rx.el.th(
                        "Created",
                        class_name="px-4 py-2 text-left text-xs font-semibold text-gray-500 uppercase hidden lg:table-cell",
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
                    UsersState.page_rows,
                    lambda u: rx.el.tr(
                        rx.el.td(
                            u["username"],
                            class_name="px-4 py-3 text-sm text-gray-900 font-medium",
                        ),
                        rx.el.td(
                            u["full_name"],
                            class_name="px-4 py-3 text-sm text-gray-800",
                        ),
                        rx.el.td(
                            u["email"],
                            class_name="px-4 py-3 text-sm text-gray-600 hidden md:table-cell",
                        ),
                        rx.el.td(
                            rx.el.span(
                                rx.cond(u["is_active"], "Active", "Inactive"),
                                class_name=rx.cond(
                                    u["is_active"],
                                    "px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-700",
                                    "px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-600",
                                ),
                            ),
                            class_name="px-4 py-3",
                        ),
                        rx.el.td(
                            u["created_at"],
                            class_name="px-4 py-3 text-sm text-gray-500 hidden lg:table-cell",
                        ),
                        rx.el.td(
                            rx.el.div(
                                rx.el.button(
                                    rx.icon("pencil", class_name="h-3.5 w-3.5"),
                                    on_click=lambda: UsersState.open_edit(
                                        u["id"]
                                    ),
                                    class_name="px-2 py-1.5 bg-blue-50 hover:bg-blue-100 text-blue-700 rounded-lg",
                                    title="Edit",
                                ),
                                rx.el.button(
                                    rx.icon(
                                        "key-round", class_name="h-3.5 w-3.5"
                                    ),
                                    on_click=lambda: (
                                        UsersState.open_change_password(u["id"])
                                    ),
                                    class_name="px-2 py-1.5 bg-amber-50 hover:bg-amber-100 text-amber-700 rounded-lg",
                                    title="Change Password",
                                ),
                                rx.el.button(
                                    rx.icon(
                                        "trash-2", class_name="h-3.5 w-3.5"
                                    ),
                                    on_click=lambda: UsersState.confirm_delete(
                                        u["id"]
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
            f"Page {UsersState.page + 1} of {UsersState.total_pages} • {UsersState.total_count} users",
            class_name="text-xs text-gray-500",
        ),
        rx.el.div(
            secondary_btn(
                rx.icon("chevron-left", class_name="h-4 w-4"),
                "Prev",
                type="button",
                on_click=UsersState.prev_page,
            ),
            secondary_btn(
                "Next",
                rx.icon("chevron-right", class_name="h-4 w-4"),
                type="button",
                on_click=UsersState.next_page,
            ),
            class_name="flex gap-2",
        ),
        class_name="flex items-center justify-between px-4 py-3 border-t border-gray-200",
    )


def _form_modal() -> rx.Component:
    return modal(
        UsersState.form_open,
        rx.cond(UsersState.editing_id != 0, "Edit User", "Add User").to(str),
        UsersState.close_form,
        error_banner(UsersState.form_error),
        rx.el.div(
            form_field(
                "Username *",
                rx.el.input(
                    on_change=UsersState.set_form_username.debounce(200),
                    default_value=UsersState.form_username,
                    class_name=INPUT_CLS,
                ),
            ),
            form_field(
                "Full Name *",
                rx.el.input(
                    on_change=UsersState.set_form_full_name.debounce(200),
                    default_value=UsersState.form_full_name,
                    class_name=INPUT_CLS,
                ),
            ),
            class_name="grid grid-cols-1 md:grid-cols-2 gap-4 mb-3",
        ),
        form_field(
            "Email *",
            rx.el.input(
                type="email",
                on_change=UsersState.set_form_email.debounce(200),
                default_value=UsersState.form_email,
                class_name=INPUT_CLS,
            ),
        ),
        rx.el.div(class_name="h-3"),
        rx.el.div(
            form_field(
                rx.cond(
                    UsersState.editing_id != 0,
                    "New Password (leave blank to keep)",
                    "Password *",
                ).to(str),
                rx.el.input(
                    type="password",
                    on_change=UsersState.set_form_password,
                    default_value=UsersState.form_password,
                    class_name=INPUT_CLS,
                ),
            ),
            form_field(
                "Confirm Password",
                rx.el.input(
                    type="password",
                    on_change=UsersState.set_form_confirm,
                    default_value=UsersState.form_confirm,
                    class_name=INPUT_CLS,
                ),
            ),
            class_name="grid grid-cols-1 md:grid-cols-2 gap-4",
        ),
        rx.el.div(class_name="h-3"),
        rx.el.label(
            rx.el.input(
                type="checkbox",
                checked=UsersState.form_is_active,
                on_change=UsersState.toggle_form_active,
                class_name="h-4 w-4 rounded border-gray-300 text-blue-600",
            ),
            rx.el.span(
                "Active",
                class_name="text-sm text-gray-700",
            ),
            class_name="inline-flex items-center gap-2 cursor-pointer",
        ),
        rx.el.div(
            secondary_btn(
                "Cancel", type="button", on_click=UsersState.close_form
            ),
            primary_btn(
                rx.icon("save", class_name="h-4 w-4"),
                "Save User",
                type="button",
                on_click=UsersState.save_user,
            ),
            class_name="flex justify-end gap-2 mt-5",
        ),
    )


def _password_modal() -> rx.Component:
    return modal(
        UsersState.pwd_open,
        "Change Password",
        UsersState.close_change_password,
        error_banner(UsersState.pwd_error),
        form_field(
            "Current Password *",
            rx.el.input(
                type="password",
                on_change=UsersState.set_pwd_current,
                default_value=UsersState.pwd_current,
                class_name=INPUT_CLS,
            ),
        ),
        rx.el.div(class_name="h-3"),
        form_field(
            "New Password *",
            rx.el.input(
                type="password",
                on_change=UsersState.set_pwd_new,
                default_value=UsersState.pwd_new,
                class_name=INPUT_CLS,
            ),
        ),
        rx.el.div(class_name="h-3"),
        form_field(
            "Confirm New Password *",
            rx.el.input(
                type="password",
                on_change=UsersState.set_pwd_confirm,
                default_value=UsersState.pwd_confirm,
                class_name=INPUT_CLS,
            ),
        ),
        rx.el.div(
            secondary_btn(
                "Cancel",
                type="button",
                on_click=UsersState.close_change_password,
            ),
            primary_btn(
                rx.icon("save", class_name="h-4 w-4"),
                "Update Password",
                type="button",
                on_click=UsersState.save_password,
            ),
            class_name="flex justify-end gap-2 mt-5",
        ),
    )


def users_page() -> rx.Component:
    return page_shell(
        "Users",
        [("Home", "/dashboard"), ("Users", "/users")],
        loading_overlay(UsersState.loading),
        success_banner(UsersState.success_message),
        rx.el.div(
            _toolbar(),
            _table(),
            _pagination(),
            class_name="bg-white rounded-lg border border-gray-200 overflow-hidden",
        ),
        _form_modal(),
        _password_modal(),
        confirm_dialog(
            UsersState.delete_open,
            "Delete User?",
            "This action cannot be undone. Are you sure you want to delete this admin user?",
            UsersState.delete_user,
            UsersState.cancel_delete,
        ),
    )
