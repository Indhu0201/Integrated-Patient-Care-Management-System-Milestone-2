import reflex as rx


def modal(
    is_open: rx.Var,
    title: str,
    on_close: rx.event.EventType,
    *body: rx.Component,
    footer: rx.Component | None = None,
    width: str = "max-w-2xl",
) -> rx.Component:
    return rx.cond(
        is_open,
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.h3(
                        title,
                        class_name="text-lg font-semibold text-gray-900",
                    ),
                    rx.el.button(
                        rx.icon("x", class_name="h-5 w-5"),
                        type="button",
                        on_click=on_close,
                        class_name="text-gray-400 hover:text-gray-600",
                    ),
                    class_name="flex items-center justify-between px-6 py-4 border-b border-gray-200",
                ),
                rx.el.div(
                    *body, class_name="px-6 py-5 max-h-[70vh] overflow-y-auto"
                ),
                rx.cond(
                    footer is not None,
                    rx.el.div(
                        footer if footer is not None else rx.fragment(),
                        class_name="px-6 py-4 border-t border-gray-200 bg-gray-50 flex items-center justify-end gap-2",
                    ),
                    rx.fragment(),
                ),
                class_name=f"bg-white rounded-lg shadow-xl w-full {width} mx-4",
            ),
            class_name="fixed inset-0 bg-black/40 backdrop-blur-xs flex items-center justify-center z-40",
        ),
        rx.fragment(),
    )


def confirm_dialog(
    is_open: rx.Var,
    title: str,
    message: str,
    on_confirm: rx.event.EventType,
    on_cancel: rx.event.EventType,
    confirm_label: str = "Delete",
) -> rx.Component:
    return rx.cond(
        is_open,
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.icon(
                            "triangle-alert", class_name="h-6 w-6 text-red-600"
                        ),
                        class_name="h-12 w-12 rounded-full bg-red-100 flex items-center justify-center",
                    ),
                    rx.el.div(
                        rx.el.h3(
                            title,
                            class_name="text-lg font-semibold text-gray-900",
                        ),
                        rx.el.p(
                            message, class_name="text-sm text-gray-600 mt-1"
                        ),
                        class_name="flex-1",
                    ),
                    class_name="flex gap-4 px-6 py-5",
                ),
                rx.el.div(
                    rx.el.button(
                        "Cancel",
                        type="button",
                        on_click=on_cancel,
                        class_name="px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-50",
                    ),
                    rx.el.button(
                        confirm_label,
                        type="button",
                        on_click=on_confirm,
                        class_name="px-4 py-2 bg-red-600 text-white rounded-lg text-sm font-medium hover:bg-red-700",
                    ),
                    class_name="px-6 py-4 border-t border-gray-200 bg-gray-50 flex items-center justify-end gap-2",
                ),
                class_name="bg-white rounded-lg shadow-xl w-full max-w-md mx-4",
            ),
            class_name="fixed inset-0 bg-black/40 backdrop-blur-xs flex items-center justify-center z-50",
        ),
        rx.fragment(),
    )


INPUT_CLS = "w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-hidden focus:ring-2 focus:ring-blue-500 bg-white"
LABEL_CLS = "text-sm font-medium text-gray-700 mb-1 block"
SELECT_CLS = INPUT_CLS + " appearance-none"


def form_field(label: str, *body: rx.Component) -> rx.Component:
    return rx.el.div(
        rx.el.label(label, class_name=LABEL_CLS),
        *body,
        class_name="flex flex-col",
    )


def primary_btn(*children, **kwargs) -> rx.Component:
    kwargs.setdefault(
        "class_name",
        "px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium flex items-center gap-2",
    )
    return rx.el.button(*children, **kwargs)


def secondary_btn(*children, **kwargs) -> rx.Component:
    kwargs.setdefault(
        "class_name",
        "px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-50 flex items-center gap-2",
    )
    return rx.el.button(*children, **kwargs)


def danger_btn(*children, **kwargs) -> rx.Component:
    kwargs.setdefault(
        "class_name",
        "px-3 py-1.5 bg-red-50 border border-red-200 text-red-700 rounded-lg text-xs font-medium hover:bg-red-100 flex items-center gap-1",
    )
    return rx.el.button(*children, **kwargs)


def error_banner(message: rx.Var) -> rx.Component:
    return rx.cond(
        message != "",
        rx.el.div(
            rx.icon("triangle-alert", class_name="h-4 w-4 text-red-600"),
            rx.el.p(message, class_name="text-sm text-red-700"),
            class_name="flex items-center gap-2 bg-red-50 border border-red-200 rounded-lg px-3 py-2 mb-3",
        ),
        rx.fragment(),
    )


def success_banner(message: rx.Var) -> rx.Component:
    return rx.cond(
        message != "",
        rx.el.div(
            rx.icon("circle-check", class_name="h-4 w-4 text-green-600"),
            rx.el.p(message, class_name="text-sm text-green-700"),
            class_name="flex items-center gap-2 bg-green-50 border border-green-200 rounded-lg px-3 py-2 mb-3",
        ),
        rx.fragment(),
    )
