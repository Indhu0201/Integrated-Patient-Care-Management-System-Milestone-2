import reflex as rx


def _error_layout(
    code: str, title: str, message: str, icon: str, color: str
) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.icon(icon, class_name=f"h-10 w-10 {color}"),
                class_name=f"h-20 w-20 rounded-full flex items-center justify-center bg-white border border-gray-200",
            ),
            rx.el.h1(
                code, class_name="text-6xl font-extrabold text-gray-900 mt-6"
            ),
            rx.el.h2(
                title, class_name="text-xl font-semibold text-gray-800 mt-2"
            ),
            rx.el.p(
                message,
                class_name="text-sm text-gray-500 mt-2 max-w-md text-center",
            ),
            rx.el.a(
                rx.icon("arrow-left", class_name="h-4 w-4"),
                "Back to Dashboard",
                href="/dashboard",
                class_name="mt-6 flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700",
            ),
            class_name="flex flex-col items-center",
        ),
        class_name="min-h-screen flex items-center justify-center bg-gray-50 font-['Inter'] p-6",
    )


def not_found_page() -> rx.Component:
    return _error_layout(
        "404",
        "Page Not Found",
        "The page you requested does not exist or has been moved.",
        "map",
        "text-blue-600",
    )


def server_error_page() -> rx.Component:
    return _error_layout(
        "500",
        "Server Error",
        "Something went wrong on our end. Please try again shortly.",
        "server-crash",
        "text-red-600",
    )
