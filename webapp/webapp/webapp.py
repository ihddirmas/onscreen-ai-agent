import reflex as rx


def index() -> rx.Component:
    return rx.center(rx.text("Parakeet — under construction"), height="100vh")


app = rx.App()
app.add_page(index, route="/")
