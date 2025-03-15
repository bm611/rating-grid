import reflex as rx
from typing import Dict, Any
from .state import State


def hero() -> rx.Component:
    return rx.vstack(
        rx.text("Series Guide", class_name="text-5xl tracking-wide md:text-6xl"),
        rx.text(
            "Search for your favorite TV series and discover ratings, details, and more",
            class_name="text-2xl text-gray-600 mt-14 text-center max-w-2xl md:text-3xl",
        ),
        rx.hstack(
            rx.input(
                placeholder="Search for a tv series",
                class_name="w-full h-14 px-4 py-2 text-lg md:text-2xl rounded-md border-2 border-black",
            ),
            rx.button(
                "Search",
                class_name="h-14 px-4 py-2 text-lg md:text-2xl rounded-md",
            ),
            class_name="w-full",
        ),
        rx.text(
            "Powered by The Movie Database (TMDb) and Open Movie Database (OMDb)",
            class_name="text-sm text-center md:text-lg text-gray-600 mt-4",
        ),
        class_name="flex flex-col justify-center items-center mb-14 mt-4",
    )


def movie_card(show: Dict[str, Any]) -> rx.Component:
    return rx.box(
        rx.link(
            rx.image(
                src=show["poster_path"],
                class_name="w-full h-3/4 object-cover rounded-2xl mb-4",
            ),
            class_name="transition-opacity duration-300 ease-in-out hover:opacity-70",
        ),
        rx.text(
            show["name"], class_name="mt-2 text-sm md:text-base tracking-wide truncate"
        ),
        rx.hstack(
            rx.image(
                src="https://upload.wikimedia.org/wikipedia/commons/6/69/IMDB_Logo_2016.svg",
                width="36px",
                height="18px",
                html_width="36px",
                html_height="18px",
            ),
            rx.cond(
                show["imdb_rating"],
                rx.text(
                    show["imdb_rating"],
                    class_name="text-gray-500 text-xs md:text-sm",
                ),
                rx.text(
                    "N/A",
                    class_name="text-gray-500 text-xs md:text-sm",
                ),
            ),
            spacing="2",
            align_items="center",
            class_name="mt-2 flex items-center",
        ),
        class_name="w-full rounded-lg overflow-hidden transition-shadow duration-300",
    )


def popular():
    return rx.vstack(
        rx.heading(
            "Popular TV Shows", class_name="text-3xl tracking-wide md:text-4xl mb-8"
        ),
        rx.flex(
            rx.foreach(
                State.popular_tv_shows,
                movie_card,
            ),
            class_name="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-4 xl:grid-cols-4 gap-6",
            wrap="wrap",
        ),
        on_mount=State.fetch_popular_tv_shows,
    )
