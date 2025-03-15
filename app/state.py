import reflex as rx
from typing import List, Dict, Any
from .tmdb_api import TMDbAPI


class State(rx.State):
    """Application state for managing TV show data and user interactions."""

    # Popular TV shows data
    popular_tv_shows: List[Dict[str, Any]] = []
    is_loading_popular: bool = False
    error_message: str = ""

    # TV series details data
    series_details: Dict[str, Any] = {
        "title": "",
        "poster_path": "",
        "vote_average": 0,
        "imdb_rating": "",
        "genres": [],
        "overview": "",
        "number_of_seasons": 0,
        "number_of_episodes": 0,
        "vote_count": 0,
        "networks": [],
    }
    is_loading_details: bool = False

    # Sample TV series for demo
    sample_series_title: str = "Severance"

    # TMDb API client instance
    _tmdb_api = None

    def on_load(self):
        """Initialize API client when state is loaded."""
        try:
            self._tmdb_api = TMDbAPI()
        except ValueError as e:
            self.error_message = str(e)

    def fetch_popular_tv_shows(self):
        """Fetch popular TV shows from TMDb API."""
        self.is_loading_popular = True
        self.error_message = ""

        try:
            # Initialize API client if needed
            if not self._tmdb_api:
                self._tmdb_api = TMDbAPI()

            # Use the existing get_trending_tv_series method
            response = self._tmdb_api.get_trending_tv_series(
                time_window="week", page=1, limit=12
            )

            # Check for errors
            if "error" in response:
                self.error_message = response["error"]
                return

            # Extract the results
            self.popular_tv_shows = response.get("results", [])
        except Exception as e:
            self.error_message = f"Failed to fetch popular TV shows: {str(e)}"
        finally:
            self.is_loading_popular = False

    def fetch_series_details(self):
        """Fetch details for the sample TV series."""
        self.is_loading_details = True
        self.error_message = ""

        try:
            # Initialize API client if needed
            if not self._tmdb_api:
                self._tmdb_api = TMDbAPI()

            # Use the get_tv_details method
            response = self._tmdb_api.get_tv_details(self.sample_series_title)

            # Check for errors
            if "error" in response:
                self.error_message = response["error"]
                return

            # Store the series details
            self.series_details = response

            # Also fetch episode ratings
            episodes_response = self._tmdb_api.get_all_episodes_ratings(
                self.sample_series_title
            )
            if "error" not in episodes_response and "seasons" in episodes_response:
                self.series_details["seasons_data"] = episodes_response["seasons"]
        except Exception as e:
            self.error_message = f"Failed to fetch series details: {str(e)}"
        finally:
            self.is_loading_details = False
