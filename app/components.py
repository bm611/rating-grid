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
        rx.hstack(
            rx.icon("trending-up", color="blue", size=42),
            rx.text(
                "Trending",
                class_name="text-3xl font-regular tracking-wide md:text-4xl",
            ),
            spacing="2",
            align_items="center",
            class_name="mb-4",
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


def movie_detail():
    return rx.vstack(
        rx.cond(
            State.is_loading_details,
            # Loading state
            rx.center(
                rx.spinner(size="3", color="black", thickness="4px"),
                class_name="h-[80vh]",
            ),
            # Content when loaded
            rx.cond(
                State.error_message,
                # Error state
                rx.center(
                    rx.vstack(
                        rx.icon("file-warning", size=48, color="red"),
                        rx.text(State.error_message, class_name="text-xl text-red-500"),
                        spacing="4",
                        class_name="p-8 border-4 border-black bg-red-100",
                    ),
                    class_name="h-[80vh]",
                ),
                # Series details
                rx.vstack(
                    # Header with title and ratings - using Tailwind for responsive layout
                    rx.box(
                        rx.box(
                            # Poster and details in a flex container
                            rx.box(
                                rx.image(
                                    src=f"https://image.tmdb.org/t/p/w500{State.series_details['poster_path']}",
                                    class_name="w-full h-full object-cover rounded-lg",
                                ),
                                class_name="w-32 h-48 md:w-48 md:h-72 shadow-md overflow-hidden rounded-lg",
                            ),
                            # Title and details
                            rx.vstack(
                                rx.heading(
                                    State.series_details["title"],
                                    class_name="text-xl md:text-3xl lg:text-4xl font-semibold text-center",
                                ),
                                # Ratings
                                rx.hstack(
                                    # TMDb rating
                                    rx.hstack(
                                        rx.image(
                                            src="https://www.themoviedb.org/assets/2/v4/logos/v2/blue_square_1-5bdc75aaebeb75dc7ae79426ddd9be3b2be1e342510f8202baf6bffa71d7f5c4.svg",
                                            width="24px",
                                            height="24px",
                                            html_width="24px",
                                            html_height="24px",
                                            class_name="rounded",
                                        ),
                                        rx.text(
                                            f"{State.series_details['vote_average']}",
                                            class_name="text-gray-800 text-xs md:text-sm font-medium",
                                        ),
                                        spacing="2",
                                        align_items="center",
                                        class_name="bg-blue-50 px-3 py-1 shadow-sm min-w-[80px] h-[36px] flex justify-center rounded-full",
                                    ),
                                    # IMDb rating
                                    rx.hstack(
                                        rx.image(
                                            src="https://upload.wikimedia.org/wikipedia/commons/6/69/IMDB_Logo_2016.svg",
                                            width="36px",
                                            height="18px",
                                            html_width="36px",
                                            html_height="18px",
                                        ),
                                        rx.cond(
                                            State.series_details["imdb_rating"],
                                            rx.text(
                                                State.series_details["imdb_rating"],
                                                class_name="text-gray-800 text-xs md:text-sm font-medium",
                                            ),
                                            rx.text(
                                                "N/A",
                                                class_name="text-gray-800 text-xs md:text-sm font-medium",
                                            ),
                                        ),
                                        spacing="2",
                                        align_items="center",
                                        class_name="bg-yellow-50 px-3 py-1 shadow-sm min-w-[80px] h-[36px] flex justify-center rounded-full",
                                    ),
                                    spacing="4",
                                    class_name="mt-4",
                                ),
                                align_items="start",
                                spacing="2",
                                class_name="ml-3 md:ml-6",
                            ),
                            class_name="flex flex-col md:flex-row items-center md:items-start space-y-4 md:space-y-0 md:space-x-4 w-full px-1",
                        ),
                        class_name="w-full",
                    ),
                    # Overview
                    rx.vstack(
                        rx.heading(
                            "Overview",
                            class_name="text-xl md:text-2xl font-semibold",
                        ),
                        rx.text(
                            State.series_details["overview"],
                            class_name="text-md tracking-wide md:text-lg text-gray-700",
                        ),
                        align_items="start",
                        spacing="4",
                        class_name="mt-8 p-4 md:p-6 bg-white rounded-xl shadow-sm",
                    ),
                    # Stats - using Tailwind for responsive layout
                    rx.box(
                        rx.box(
                            # Seasons
                            rx.vstack(
                                rx.text(
                                    "Seasons",
                                    class_name="text-md md:text-lg font-medium text-gray-600",
                                ),
                                rx.text(
                                    State.series_details["number_of_seasons"],
                                    class_name="text-xl md:text-3xl font-semibold",
                                ),
                                class_name="p-3 md:p-4 bg-blue-50 rounded-xl shadow-sm flex-1 text-center",
                            ),
                            # Episodes
                            rx.vstack(
                                rx.text(
                                    "Episodes",
                                    class_name="text-md md:text-lg font-medium text-gray-600",
                                ),
                                rx.text(
                                    State.series_details["number_of_episodes"],
                                    class_name="text-xl md:text-3xl font-semibold",
                                ),
                                class_name="p-3 md:p-4 bg-green-50 rounded-xl shadow-sm flex-1 text-center",
                            ),
                            # Vote Count
                            rx.vstack(
                                rx.text(
                                    "Vote Count",
                                    class_name="text-md md:text-lg font-medium text-gray-600",
                                ),
                                rx.text(
                                    State.series_details["vote_count"],
                                    class_name="text-xl md:text-3xl font-semibold",
                                ),
                                class_name="p-3 md:p-4 bg-purple-50 rounded-xl shadow-sm flex-1 text-center",
                            ),
                            class_name="flex flex-col md:flex-row space-y-3 md:space-y-0 md:space-x-4 w-full",
                        ),
                        class_name="w-full mt-6 px-1",
                    ),
                    # Season Highlights (if available)
                    rx.cond(
                        State.series_details.contains("seasons_data"),
                        rx.vstack(
                            rx.heading(
                                "Season Highlights",
                                class_name="text-xl md:text-2xl font-semibold mt-6",
                            ),
                            rx.text(
                                "Top rated episodes from each season",
                                class_name="text-sm md:text-md text-gray-600 mb-2",
                            ),
                            rx.box(
                                rx.text(
                                    "Season data available! Click to explore seasons and episodes.",
                                    class_name="p-4 bg-yellow-50 rounded-lg shadow-sm text-gray-700",
                                ),
                                class_name="w-full",
                            ),
                            align_items="start",
                            class_name="w-full px-1",
                        ),
                        rx.box(),  # Empty if no season data
                    ),
                    align_items="start",
                    spacing="0",
                    class_name="w-full max-w-5xl p-3 md:p-6",
                ),
            ),
        ),
        on_mount=State.fetch_series_details,
        class_name="min-h-screen",
    )
