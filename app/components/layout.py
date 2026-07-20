import reflex as rx
from app.components.sidebar import sidebar
from app.states.auth_state import AuthState


def _breadcrumbs(items: list[tuple[str, str]]) -> rx.Component:
    def _crumb(item: tuple[str, str], is_last: bool) -> rx.Component:
        label, href = item
        return rx.el.div(
            rx.cond(
                is_last,
                rx.el.span(label, class_name="text-gray-900 font-semibold"),
                rx.el.a(
                    label, href=href, class_name="text-blue-600 hover:underline"
                ),
            ),
            rx.cond(
                is_last,
                rx.fragment(),
                rx.icon(
                    "chevron-right", class_name="h-4 w-4 text-gray-400 mx-2"
                ),
            ),
            class_name="flex items-center",
        )

    children = []
    for idx, item in enumerate(items):
        children.append(_crumb(item, idx == len(items) - 1))
    return rx.el.nav(*children, class_name="flex items-center text-sm")


def topbar(title: str, breadcrumb_items: list[tuple[str, str]]) -> rx.Component:
    return rx.el.header(
        rx.el.div(
            rx.el.div(
                rx.el.h1(title, class_name="text-xl font-bold text-gray-900"),
                _breadcrumbs(breadcrumb_items),
                class_name="flex flex-col gap-1",
            ),
            rx.el.div(
                rx.el.div(
                    rx.icon("bell", class_name="h-5 w-5 text-gray-600"),
                    class_name="p-2 rounded-lg bg-gray-100 hover:bg-gray-200 cursor-pointer",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.icon("user", class_name="h-5 w-5 text-white"),
                        class_name="h-9 w-9 rounded-full bg-blue-600 flex items-center justify-center",
                    ),
                    rx.el.div(
                        rx.el.p(
                            AuthState.admin_full_name,
                            class_name="text-sm font-semibold text-gray-900 leading-tight",
                        ),
                        rx.el.p(
                            "Administrator", class_name="text-xs text-gray-500"
                        ),
                        class_name="hidden sm:block",
                    ),
                    class_name="flex items-center gap-2",
                ),
                class_name="flex items-center gap-4",
            ),
            class_name="flex items-center justify-between px-6 py-4",
        ),
        class_name="bg-white border-b border-gray-200 sticky top-0 z-10",
    )


def page_shell(
    title: str,
    breadcrumb_items: list[tuple[str, str]],
    *content: rx.Component,
) -> rx.Component:
    return rx.el.div(
        rx.cond(
            AuthState.is_authenticated,
            rx.el.div(
                sidebar(),
                rx.el.div(
                    topbar(title, breadcrumb_items),
                    rx.el.main(
                        *content,
                        class_name="p-6 flex flex-col gap-6",
                    ),
                    class_name="flex-1 min-w-0 bg-gray-50 min-h-screen",
                ),
                class_name="flex bg-gray-50 min-h-screen",
            ),
            rx.el.div(
                rx.el.a(
                    "You must be logged in. Click here to log in.",
                    href="/",
                    class_name="text-blue-600 underline",
                ),
                class_name="min-h-screen flex items-center justify-center bg-gray-50",
            ),
        ),
        class_name="font-['Inter']",
    )


def loading_overlay(is_loading: rx.Var) -> rx.Component:
    return rx.cond(
        is_loading,
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    class_name="animate-spin rounded-full h-10 w-10 border-4 border-blue-200 border-t-blue-600"
                ),
                rx.el.p("Loading...", class_name="text-sm text-gray-600 mt-3"),
                class_name="bg-white rounded-lg shadow-lg px-8 py-6 flex flex-col items-center",
            ),
            class_name="fixed inset-0 bg-black/20 backdrop-blur-xs flex items-center justify-center z-50",
        ),
        rx.fragment(),
    )
