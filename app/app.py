"""Welcome to Reflex! This file outlines the steps to create a basic app."""

import reflex as rx
from .components import hero, popular, movie_detail


@rx.page(route="/", title="Rating Grid")
def index() -> rx.Component:
    # Welcome Page (Index)
    return rx.container(
        hero(),
        popular(),
        class_name="flex justify-center items-center",
        size="4",
    )


@rx.page(route="movie/demo", title="Movie Demo")
def movie_demo() -> rx.Component:
    return rx.container(
        movie_detail(),
        class_name="flex justify-center items-center",
        size="4",
    )


style = {
    "font_family": "Grotesk",
}

app = rx.App(
    style=rx.Style(style),
    stylesheets=["/fonts/font.css"],
    theme=rx.theme(
        appearance="light",
    ),
)
