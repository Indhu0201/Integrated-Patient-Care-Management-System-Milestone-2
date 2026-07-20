import reflex as rx

from app.components.layout import loading_overlay, page_shell
from app.components.modal import (
    INPUT_CLS,
    SELECT_CLS,
    error_banner,
    form_field,
    primary_btn,
    secondary_btn,
    success_banner,
)
from app.states.settings_state import SettingsState


def _hospital_card() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h3(
                "Hospital Information",
                class_name="text-base font-semibold text-gray-900",
            ),
            rx.el.p(
                "General information about your hospital shown on reports and PDFs.",
                class_name="text-xs text-gray-500 mt-0.5",
            ),
            class_name="px-5 py-3 border-b border-gray-200",
        ),
        rx.el.div(
            form_field(
                "Hospital Name *",
                rx.el.input(
                    on_change=SettingsState.set_hospital_name.debounce(400),
                    default_value=SettingsState.hospital_name,
                    class_name=INPUT_CLS,
                ),
            ),
            rx.el.div(class_name="h-3"),
            form_field(
                "Address *",
                rx.el.textarea(
                    rows="2",
                    on_change=SettingsState.set_hospital_address.debounce(400),
                    default_value=SettingsState.hospital_address,
                    class_name=INPUT_CLS,
                ),
            ),
            class_name="p-5",
        ),
        class_name="bg-white rounded-lg border border-gray-200 overflow-hidden",
    )


def _contact_card() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h3(
                "Contact Details",
                class_name="text-base font-semibold text-gray-900",
            ),
            class_name="px-5 py-3 border-b border-gray-200",
        ),
        rx.el.div(
            form_field(
                "Contact Email *",
                rx.el.input(
                    type="email",
                    on_change=SettingsState.set_contact_email.debounce(400),
                    default_value=SettingsState.contact_email,
                    class_name=INPUT_CLS,
                ),
            ),
            form_field(
                "Contact Phone *",
                rx.el.input(
                    on_change=SettingsState.set_contact_phone.debounce(400),
                    default_value=SettingsState.contact_phone,
                    class_name=INPUT_CLS,
                ),
            ),
            class_name="grid grid-cols-1 md:grid-cols-2 gap-4 p-5",
        ),
        class_name="bg-white rounded-lg border border-gray-200 overflow-hidden",
    )


def _logo_card() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h3(
                "Hospital Logo",
                class_name="text-base font-semibold text-gray-900",
            ),
            rx.el.p(
                "PNG or JPG recommended. Used on generated PDF reports.",
                class_name="text-xs text-gray-500 mt-0.5",
            ),
            class_name="px-5 py-3 border-b border-gray-200",
        ),
        rx.el.div(
            rx.cond(
                SettingsState.hospital_logo != "",
                rx.el.div(
                    rx.image(
                        src=rx.get_upload_url(SettingsState.hospital_logo),
                        class_name="h-20 w-20 rounded-lg object-cover border border-gray-200",
                    ),
                    rx.el.div(
                        rx.el.p(
                            SettingsState.hospital_logo,
                            class_name="text-xs text-gray-600 break-all",
                        ),
                        secondary_btn(
                            rx.icon("x", class_name="h-3.5 w-3.5"),
                            "Remove",
                            type="button",
                            on_click=SettingsState.clear_logo,
                        ),
                        class_name="flex flex-col gap-2",
                    ),
                    class_name="flex items-center gap-4 mb-4",
                ),
                rx.fragment(),
            ),
            rx.upload.root(
                rx.el.div(
                    rx.icon("upload", class_name="h-4 w-4 text-blue-600"),
                    rx.el.p(
                        "Drag & drop or click to upload logo",
                        class_name="text-sm text-gray-600",
                    ),
                    class_name="flex items-center gap-2 justify-center",
                ),
                id="settings_logo_upload",
                on_drop=SettingsState.handle_logo_upload(
                    rx.upload_files(upload_id="settings_logo_upload")
                ),
                multiple=False,
                accept={"image/*": [".png", ".jpg", ".jpeg", ".svg"]},
                class_name="border-2 border-dashed border-gray-300 rounded-lg p-4 cursor-pointer hover:border-blue-400 bg-gray-50",
            ),
            class_name="p-5",
        ),
        class_name="bg-white rounded-lg border border-gray-200 overflow-hidden",
    )


def _preferences_card() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h3(
                "Preferences",
                class_name="text-base font-semibold text-gray-900",
            ),
            class_name="px-5 py-3 border-b border-gray-200",
        ),
        rx.el.div(
            form_field(
                "Theme",
                rx.el.select(
                    rx.foreach(
                        SettingsState.theme_options,
                        lambda t: rx.el.option(t.capitalize(), value=t),
                    ),
                    value=SettingsState.theme,
                    on_change=SettingsState.set_theme,
                    class_name=SELECT_CLS,
                ),
            ),
            form_field(
                "Timezone",
                rx.el.select(
                    rx.foreach(
                        SettingsState.timezone_options,
                        lambda t: rx.el.option(t, value=t),
                    ),
                    value=SettingsState.timezone,
                    on_change=SettingsState.set_timezone,
                    class_name=SELECT_CLS,
                ),
            ),
            class_name="grid grid-cols-1 md:grid-cols-2 gap-4 p-5",
        ),
        class_name="bg-white rounded-lg border border-gray-200 overflow-hidden",
    )


def _stats_card() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.p(
                "Total Reports Generated",
                class_name="text-xs text-gray-500 uppercase tracking-wide",
            ),
            rx.el.p(
                SettingsState.total_reports.to_string(),
                class_name="text-2xl font-bold text-gray-900 mt-1",
            ),
            class_name="p-5",
        ),
        class_name="bg-white rounded-lg border border-gray-200",
    )


def settings_page() -> rx.Component:
    return page_shell(
        "Settings",
        [("Home", "/dashboard"), ("Settings", "/settings")],
        loading_overlay(SettingsState.loading),
        error_banner(SettingsState.form_error),
        success_banner(SettingsState.success_message),
        rx.el.div(
            rx.el.div(
                _hospital_card(),
                _contact_card(),
                _preferences_card(),
                class_name="flex flex-col gap-4 lg:col-span-2",
            ),
            rx.el.div(
                _logo_card(),
                _stats_card(),
                class_name="flex flex-col gap-4",
            ),
            class_name="grid grid-cols-1 lg:grid-cols-3 gap-4",
        ),
        rx.el.div(
            primary_btn(
                rx.icon("save", class_name="h-4 w-4"),
                "Save Settings",
                type="button",
                on_click=SettingsState.save_settings,
            ),
            class_name="flex justify-end",
        ),
    )
