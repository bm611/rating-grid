import requests
import json


def get_popular_tv_series():
    # Replace 'YOUR_API_KEY' with your actual TMDB API key
    api_key = "89926f8fdd08dc8a303c03f5c168cac8"
    url = f"https://api.themoviedb.org/3/trending/tv/week?api_key={api_key}&language=en-US&page=1"

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        # Extract just the names of the top 10 TV series
        tv_series_names = [show["name"] for show in data["results"][:10]]

        # Convert to JSON format
        json_output = json.dumps(tv_series_names, indent=4)
        return json_output
    else:
        return json.dumps({"error": f"Failed to fetch data: {response.status_code}"})


if __name__ == "__main__":
    popular_shows = get_popular_tv_series()
    print(popular_shows)
