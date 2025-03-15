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
            rx.vstack(
                # Card image container with neo-brutalist style
                rx.box(
                    rx.image(
                        src=show["poster_path"],
                        class_name="w-full h-full object-cover",
                    ),
                    # Thick border characteristic of neo-brutalism without rotation
                    class_name="w-full aspect-[2/3] overflow-hidden relative border-4 border-black transition-transform duration-300",
                ),
                # Content container with bold styling
                rx.vstack(
                    # Title with bold font
                    rx.text(
                        show["name"],
                        class_name="font-bold text-smmd:text-lg tracking-wide truncate w-full text-black",
                    ),
                    # Ratings container - horizontal stack for both ratings
                    rx.hstack(
                        # TMDb rating
                        rx.hstack(
                            rx.image(
                                src="https://www.themoviedb.org/assets/2/v4/logos/v2/blue_square_1-5bdc75aaebeb75dc7ae79426ddd9be3b2be1e342510f8202baf6bffa71d7f5c4.svg",
                                width="24px",
                                height="24px",
                                html_width="24px",
                                html_height="24px",
                            ),
                            rx.text(
                                show["vote_average"],
                                class_name="text-black text-xs md:text-sm font-bold",
                            ),
                            spacing="2",
                            align_items="center",
                            class_name="bg-gray-200 px-2 py-1 border-2 border-black min-w-[80px] h-[36px] flex justify-center rounded-2xl",
                        ),
                        # IMDb rating - always displayed with N/A if missing
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
                                    class_name="text-black text-xs md:text-sm font-bold",
                                ),
                                rx.text(
                                    "N/A",
                                    class_name="text-black text-xs md:text-sm font-bold",
                                ),
                            ),
                            spacing="2",
                            align_items="center",
                            class_name="bg-yellow-200 px-2 py-1 border-2 border-black min-w-[80px] h-[36px] flex justify-center rounded-2xl",
                        ),
                        spacing="2",
                        align_items="center",
                        class_name="mt-2",
                    ),
                    align_items="start",
                    spacing="0",
                    class_name="w-full pt-3 px-1 mb-2",
                ),
                class_name="w-full",
            ),
            # Add hover effect to entire card
            class_name="no-underline text-inherit",
        ),
        # Neo-brutalist container with bold borders and background
        class_name="bg-white border-4 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] transition-all duration-300 rounded-none p-2 mb-4 hover:-translate-y-1 hover:translate-x-1",
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
            class_name="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-4 gap-6",
            wrap="wrap",
        ),
        on_mount=State.fetch_popular_tv_shows,
    )
