import reflex as rx
from typing import List, Dict, Any
from .tmdb_api import TMDbAPI


class State(rx.State):
    """Application state for managing TV show data and user interactions."""

    # Popular TV shows data
    popular_tv_shows: List[Dict[str, Any]] = []
    is_loading_popular: bool = False
    error_message: str = ""
    
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
                time_window="week", 
                page=1, 
                limit=12
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