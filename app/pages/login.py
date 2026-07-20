import reflex as rx
from app.states.auth_state import AuthState


def login_page() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            # Left branding panel
            rx.el.div(
                rx.el.div(
                    rx.icon("heart-pulse", class_name="h-12 w-12 text-white"),
                    rx.el.h1(
                        "IPCMS", class_name="text-4xl font-bold text-white mt-4"
                    ),
                    rx.el.p(
                        "Integrated Patient Care Management System",
                        class_name="text-blue-100 mt-2 text-sm",
                    ),
                    class_name="flex flex-col items-center",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.icon(
                            "shield-check", class_name="h-5 w-5 text-blue-100"
                        ),
                        rx.el.p(
                            "Secure Admin Access",
                            class_name="text-blue-50 text-sm",
                        ),
                        class_name="flex items-center gap-2",
                    ),
                    rx.el.div(
                        rx.icon("database", class_name="h-5 w-5 text-blue-100"),
                        rx.el.p(
                            "Unified EHR / Consultations / Labs",
                            class_name="text-blue-50 text-sm",
                        ),
                        class_name="flex items-center gap-2",
                    ),
                    rx.el.div(
                        rx.icon(
                            "file-text", class_name="h-5 w-5 text-blue-100"
                        ),
                        rx.el.p(
                            "Reports & Analytics",
                            class_name="text-blue-50 text-sm",
                        ),
                        class_name="flex items-center gap-2",
                    ),
                    class_name="flex flex-col gap-3 mt-10",
                ),
                class_name="hidden md:flex flex-col justify-center bg-linear-to-br from-blue-700 to-blue-900 p-12 w-1/2",
            ),
            # Right form panel
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.icon(
                            "heart-pulse", class_name="h-8 w-8 text-blue-700"
                        ),
                        rx.el.h2(
                            "Admin Login",
                            class_name="text-2xl font-bold text-gray-900 mt-2",
                        ),
                        rx.el.p(
                            "Sign in to access the management portal.",
                            class_name="text-sm text-gray-500",
                        ),
                        class_name="mb-6",
                    ),
                    rx.el.form(
                        rx.el.div(
                            rx.el.label(
                                "Username",
                                class_name="text-sm font-medium text-gray-700 mb-1 block",
                            ),
                            rx.el.input(
                                name="username",
                                placeholder="admin",
                                default_value="admin",
                                class_name="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-hidden focus:ring-2 focus:ring-blue-500",
                            ),
                            class_name="mb-4",
                        ),
                        rx.el.div(
                            rx.el.label(
                                "Password",
                                class_name="text-sm font-medium text-gray-700 mb-1 block",
                            ),
                            rx.el.input(
                                name="password",
                                type="password",
                                placeholder="••••••••",
                                default_value="admin123",
                                class_name="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-hidden focus:ring-2 focus:ring-blue-500",
                            ),
                            class_name="mb-4",
                        ),
                        rx.cond(
                            AuthState.login_error != "",
                            rx.el.div(
                                rx.icon(
                                    "triangle-alert",
                                    class_name="h-4 w-4 text-red-600",
                                ),
                                rx.el.p(
                                    AuthState.login_error,
                                    class_name="text-sm text-red-700",
                                ),
                                class_name="flex items-center gap-2 bg-red-50 border border-red-200 rounded-lg px-3 py-2 mb-4",
                            ),
                            rx.fragment(),
                        ),
                        rx.el.button(
                            rx.cond(
                                AuthState.login_loading,
                                rx.el.div(
                                    class_name="animate-spin h-4 w-4 border-2 border-white/50 border-t-white rounded-full"
                                ),
                                rx.icon("log-in", class_name="h-4 w-4"),
                            ),
                            "Sign In",
                            type="submit",
                            class_name="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2.5 rounded-lg transition-colors",
                        ),
                        rx.el.div(
                            rx.el.p(
                                "Demo credentials: admin / admin123",
                                class_name="text-xs text-gray-400 text-center mt-4",
                            ),
                        ),
                        on_submit=AuthState.handle_login,
                    ),
                    class_name="w-full max-w-sm",
                ),
                class_name="flex flex-1 items-center justify-center bg-white p-8",
            ),
            class_name="flex min-h-screen w-full",
        ),
        class_name="font-['Inter'] bg-gray-50",
    )
