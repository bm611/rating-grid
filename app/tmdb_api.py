import os
import requests
from typing import Dict, Optional, Any, List, Union
import logging
from datetime import datetime


class TMDbAPI:
    """A simplified client for The Movie Database (TMDb) API."""

    BASE_URL = "https://api.themoviedb.org/3"

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the TMDb API client.

        Args:
            api_key: TMDb API key. If not provided, will try to get from TMDB_API_KEY environment variable.
        """
        self.api_key = api_key or os.environ.get("TMDB_API_KEY")
        if not self.api_key:
            raise ValueError(
                "TMDb API key is required. Please provide it as an argument or set TMDB_API_KEY environment variable."
            )

        self.session = requests.Session()
        self.logger = logging.getLogger(__name__)

        # Initialize OMDb API client if the API key is available
        self.omdb_api = None
        try:
            self.omdb_api = OMDbAPI()
        except ValueError:
            self.logger.warning(
                "OMDb API key not found. OMDb features will be disabled."
            )

    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make a request to the TMDb API.

        Args:
            endpoint: API endpoint to request.
            params: Query parameters to include in the request.

        Returns:
            JSON response from the API.
        """
        url = f"{self.BASE_URL}{endpoint}"
        params = params or {}
        params["api_key"] = self.api_key

        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error making request to {url}: {e}")
            if hasattr(e.response, "text"):
                self.logger.error(f"Response: {e.response.text}")
            raise

    def get_external_ids(self, tv_id: int) -> Dict:
        """Get external IDs for a TV show, including IMDb ID.

        Args:
            tv_id: TMDb ID of the TV show.

        Returns:
            Dictionary containing external IDs.
        """
        endpoint = f"/tv/{tv_id}/external_ids"
        return self._make_request(endpoint)

    def get_tv_details(self, title: str) -> Dict:
        """Get details for a TV show by its title.

        Args:
            title: TV show title to search for.

        Returns:
            TV show details or error message if not found.
            Now includes IMDb ID from external IDs endpoint and ratings from OMDb.
        """
        # Search for the TV show first to get its ID
        endpoint = "/search/tv"
        params = {"query": title}
        response = self._make_request(endpoint, params)
        results = response.get("results", [])

        if not results:
            return {"error": f"TV show '{title}' not found"}

        # Get the first (most relevant) result's ID
        tv_id = results[0].get("id")

        # Get detailed information about the TV show
        endpoint = f"/tv/{tv_id}"
        tv_details = self._make_request(endpoint)

        # Get external IDs including IMDb ID
        external_ids = self.get_external_ids(tv_id)
        imdb_id = external_ids.get("imdb_id")

        result = {
            "title": tv_details.get("name"),
            "original_title": tv_details.get("original_name"),
            "first_air_date": tv_details.get("first_air_date"),
            "last_air_date": tv_details.get("last_air_date"),
            "number_of_seasons": tv_details.get("number_of_seasons"),
            "number_of_episodes": tv_details.get("number_of_episodes"),
            "vote_average": tv_details.get("vote_average"),
            "vote_count": tv_details.get("vote_count"),
            "overview": tv_details.get("overview"),
            "genres": [genre.get("name") for genre in tv_details.get("genres", [])],
            "networks": [
                network.get("name") for network in tv_details.get("networks", [])
            ],
            "poster_path": tv_details.get("poster_path"),
            "backdrop_path": tv_details.get("backdrop_path"),
            "tmdb_id": tv_id,
            "imdb_id": imdb_id,
        }

        # Get IMDb and Rotten Tomatoes ratings if OMDb API is available and we have an IMDb ID
        if self.omdb_api and imdb_id:
            try:
                omdb_ratings = self.omdb_api.get_ratings(imdb_id=imdb_id)
                if omdb_ratings:
                    result["imdb_rating"] = omdb_ratings.get("imdb_rating")
                    result["imdb_votes"] = omdb_ratings.get("imdb_votes")
                    result["rotten_tomatoes"] = omdb_ratings.get("rotten_tomatoes")
                    result["metascore"] = omdb_ratings.get("metascore")
            except Exception as e:
                self.logger.error(f"Error getting OMDb ratings: {e}")

        return result

    def get_all_episodes_ratings(self, title: str) -> Dict:
        """Get ratings for all episodes of a TV show organized by season.

        Args:
            title: TV show title.

        Returns:
            Dictionary with TV show information and episode ratings organized by season.
            Now includes IMDb ID from external IDs endpoint and ratings from OMDb.
        """
        # Search for the TV show first to get its ID
        endpoint = "/search/tv"
        params = {"query": title}
        response = self._make_request(endpoint, params)
        results = response.get("results", [])

        if not results:
            return {"error": f"TV show '{title}' not found"}

        # Get the first (most relevant) result's ID
        tv_id = results[0].get("id")

        # Get detailed information about the TV show
        endpoint = f"/tv/{tv_id}"
        tv_details = self._make_request(endpoint)

        # Get external IDs including IMDb ID
        external_ids = self.get_external_ids(tv_id)
        imdb_id = external_ids.get("imdb_id")

        result = {
            "title": tv_details.get("name"),
            "first_air_date": tv_details.get("first_air_date"),
            "vote_average": tv_details.get("vote_average"),
            "seasons": {},
            "tmdb_id": tv_id,
            "imdb_id": imdb_id,
        }

        # Get IMDb and Rotten Tomatoes ratings if OMDb API is available and we have an IMDb ID
        if self.omdb_api and imdb_id:
            try:
                omdb_ratings = self.omdb_api.get_ratings(imdb_id=imdb_id)
                if omdb_ratings:
                    result["imdb_rating"] = omdb_ratings.get("imdb_rating")
                    result["imdb_votes"] = omdb_ratings.get("imdb_votes")
                    result["rotten_tomatoes"] = omdb_ratings.get("rotten_tomatoes")
                    result["metascore"] = omdb_ratings.get("metascore")
            except Exception as e:
                self.logger.error(f"Error getting OMDb ratings: {e}")

        # Filter out special seasons (season 0)
        regular_seasons = [s for s in tv_details.get("seasons", []) if s.get("season_number", 0) > 0]

        # Get current date for comparing with air dates
        current_date = datetime.now().date()

        for season in regular_seasons:
            season_number = season.get("season_number")

            # Get season details including episodes
            endpoint = f"/tv/{tv_id}/season/{season_number}"
            season_details = self._make_request(endpoint)
            episodes = season_details.get("episodes", [])

            result["seasons"][season_number] = []

            for episode in episodes:
                air_date = episode.get("air_date")

                # Check if episode is unreleased (air date is in the future or None)
                is_unreleased = False
                if air_date:
                    try:
                        episode_date = datetime.strptime(air_date, "%Y-%m-%d").date()
                        is_unreleased = episode_date > current_date
                    except ValueError:
                        # Handle invalid date format
                        is_unreleased = True
                else:
                    # No air date means it's not released yet
                    is_unreleased = True

                episode_data = {
                    "episode": episode.get("episode_number"),
                    "title": episode.get("name"),
                    "vote_average": None
                    if is_unreleased
                    else episode.get("vote_average"),
                    "vote_count": None if is_unreleased else episode.get("vote_count"),
                    "air_date": air_date,
                    "unreleased": is_unreleased,
                }
                result["seasons"][season_number].append(episode_data)

        return result

    def get_trending_tv_series(
        self, time_window: str = "week", page: int = 1, limit: int = 10
    ) -> Dict:
        """Get trending TV series for a specific time window.

        Args:
            time_window: Time window for trending data. Options are 'day' or 'week'. Default is 'week'.
            page: Page number of results to retrieve. Default is 1.
            limit: Number of results to return. Default is 10.

        Returns:
            Dictionary containing trending TV series information including:
            - id: TMDb ID
            - name: TV series name
            - overview: Brief description
            - first_air_date: First air date
            - vote_average: Average rating on TMDb
            - poster_path: Path to poster image
            - backdrop_path: Path to backdrop image
            - popularity: Popularity score
        """
        if time_window not in ["day", "week"]:
            time_window = "week"
            self.logger.warning("Invalid time window specified. Using default: 'week'")

        endpoint = "/trending/tv/" + time_window
        params = {"language": "en-US", "page": page}

        response = self._make_request(endpoint, params)

        if not response or "results" not in response:
            return {"error": "Failed to fetch trending TV series data"}

        results = response.get("results", [])[:limit]

        # Process results to include additional information
        trending_series = []
        for show in results:
            # Get external IDs including IMDb ID
            imdb_id = None
            omdb_ratings = {}

            try:
                external_ids = self.get_external_ids(show.get("id"))
                imdb_id = external_ids.get("imdb_id")

                # Get IMDb and Rotten Tomatoes ratings if OMDb API is available and we have an IMDb ID
                if self.omdb_api and imdb_id:
                    try:
                        omdb_ratings = self.omdb_api.get_ratings(imdb_id=imdb_id)
                    except Exception as e:
                        self.logger.error(f"Error getting OMDb ratings: {e}")
            except Exception as e:
                self.logger.error(f"Error getting external IDs: {e}")

            series_data = {
                "id": show.get("id"),
                "name": " ".join(
                    word.capitalize() for word in show.get("name", "").split()
                ),
                "overview": show.get("overview"),
                "first_air_date": show.get("first_air_date"),
                "vote_average": round(show.get("vote_average", 0), 1),
                "poster_path": f"https://image.tmdb.org/t/p/w500{show.get('poster_path')}"
                if show.get("poster_path")
                else None,
                "backdrop_path": f"https://image.tmdb.org/t/p/original{show.get('backdrop_path')}"
                if show.get("backdrop_path")
                else None,
                "popularity": show.get("popularity"),
                "imdb_id": imdb_id,
            }

            # Add OMDb ratings if available
            if omdb_ratings:
                series_data["imdb_rating"] = omdb_ratings.get("imdb_rating")
                series_data["imdb_votes"] = omdb_ratings.get("imdb_votes")
                series_data["rotten_tomatoes"] = omdb_ratings.get("rotten_tomatoes")
                series_data["metascore"] = omdb_ratings.get("metascore")

            trending_series.append(series_data)

        return {
            "page": response.get("page", 1),
            "total_pages": response.get("total_pages", 1),
            "total_results": response.get("total_results", 0),
            "results": trending_series,
        }


class OMDbAPI:
    """
    A client for the OMDb API to fetch IMDb and Rotten Tomatoes ratings for TV series.

    The OMDb API is a RESTful web service to obtain movie and TV series information.
    This class provides methods to search for TV series and retrieve their ratings.
    """

    BASE_URL = "http://www.omdbapi.com/"

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the OMDb API client.

        Args:
            api_key: The API key for accessing the OMDb API. If not provided,
                    it will attempt to read from the OMDB_API_KEY environment variable.

        Raises:
            ValueError: If no API key is provided and none is found in environment variables.
        """
        self.api_key = api_key or os.environ.get("OMDB_API_KEY")

        if not self.api_key:
            raise ValueError(
                "No API key provided. Please provide an API key or set the OMDB_API_KEY environment variable."
            )

    def search_series(
        self, title: str, year: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for TV series by title.

        Args:
            title: The title of the TV series to search for.
            year: Optional year of release to narrow down the search.

        Returns:
            A list of TV series matching the search criteria.
        """
        params = {"apikey": self.api_key, "s": title, "type": "series"}

        if year:
            params["y"] = year

        response = requests.get(self.BASE_URL, params=params)
        response.raise_for_status()

        data = response.json()

        if data.get("Response") == "False":
            return []

        return data.get("Search", [])

    def get_series_details(
        self, title: Optional[str] = None, imdb_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get detailed information about a TV series, including ratings.

        Args:
            title: The title of the TV series. Either title or imdb_id must be provided.
            imdb_id: The IMDb ID of the TV series. Either title or imdb_id must be provided.

        Returns:
            A dictionary containing detailed information about the TV series.

        Raises:
            ValueError: If neither title nor imdb_id is provided.
            requests.HTTPError: If the API request fails.
        """
        if not title and not imdb_id:
            raise ValueError("Either title or imdb_id must be provided.")

        params = {
            "apikey": self.api_key,
            "type": "series",
            "plot": "short",
            "tomatoes": "true",  # Include Rotten Tomatoes data
        }

        if title:
            params["t"] = title
        elif imdb_id:
            params["i"] = imdb_id

        response = requests.get(self.BASE_URL, params=params)
        response.raise_for_status()

        data = response.json()

        if data.get("Response") == "False":
            return {}

        return data

    def get_ratings(
        self, title: Optional[str] = None, imdb_id: Optional[str] = None
    ) -> Dict[str, Union[str, float, None]]:
        """
        Get IMDb and Rotten Tomatoes ratings for a TV series.
        Handles potential typos in the title by first searching for matches.

        Args:
            title: The title of the TV series. Either title or imdb_id must be provided.
            imdb_id: The IMDb ID of the TV series. Either title or imdb_id must be provided.

        Returns:
            A dictionary containing the IMDb and Rotten Tomatoes ratings.
            If a typo correction was made, includes original_query and corrected_title fields.

        Example:
            {
                "title": "Breaking Bad",
                "year": "2008–2013",
                "imdb_rating": 9.5,
                "imdb_votes": "1,500,000",
                "rotten_tomatoes": "96%",
                "metascore": 99,
                "original_query": "Breaking Bed",  # If typo was corrected
                "corrected_title": "Breaking Bad"   # If typo was corrected
            }
        """
        # If we have a title but no IMDb ID, search first to handle potential typos
        original_title = title
        corrected_title = None

        if title and not imdb_id:
            # Try to search for the series to handle typos
            search_results = self.search_series(title)

            # If we found matches, use the first (most relevant) result's IMDb ID
            if search_results:
                imdb_id = search_results[0]["imdbID"]
                corrected_title = search_results[0]["Title"]
                # We'll continue with the imdb_id instead of the potentially misspelled title

        # Now get the series details with either the original parameters or the corrected imdb_id
        series_data = self.get_series_details(title if not imdb_id else None, imdb_id)

        if not series_data:
            return {}

        ratings = {
            "title": series_data.get("Title"),
            "year": series_data.get("Year"),
            "imdb_rating": float(series_data.get("imdbRating", 0))
            if series_data.get("imdbRating") != "N/A"
            else None,
            "imdb_votes": series_data.get("imdbVotes"),
            "metascore": int(series_data.get("Metascore", 0))
            if series_data.get("Metascore") != "N/A"
            else None,
            "imdb_id": series_data.get("imdbID"),
        }

        # Extract Rotten Tomatoes rating from the Ratings array
        rt_rating = None
        for rating in series_data.get("Ratings", []):
            if rating.get("Source") == "Rotten Tomatoes":
                rt_rating = rating.get("Value")
                break

        ratings["rotten_tomatoes"] = rt_rating

        # If we corrected the title, include that information
        if (
            original_title
            and corrected_title
            and original_title.lower() != corrected_title.lower()
        ):
            ratings["original_query"] = original_title
            ratings["corrected_title"] = corrected_title

        return ratings


# Example usage
if __name__ == "__main__":
    import json

    # Use the provided API key for testing
    api = TMDbAPI()

    # Get TV show details
    print("TV Show Details for Better Call Saul:")
    tv_details = api.get_tv_details("Better Call Saul")
    print(json.dumps(tv_details, indent=4))
    print()

    # Get all episodes with ratings for a TV series
    print("All episodes with ratings for Better Call Saul:")
    all_episodes = api.get_all_episodes_ratings("Better Call Saul")
    print(json.dumps(all_episodes, indent=4))

    # Get trending TV series
    print("\nTrending TV Series this week:")
    trending = api.get_trending_tv_series(time_window="week", limit=5)
    print(json.dumps(trending, indent=4))
