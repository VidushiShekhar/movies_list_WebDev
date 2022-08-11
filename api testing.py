import requests

API_URL = "https://api.themoviedb.org/3/search/movie"
API_KEY = "25a661dad53fcca6dc07eb9b2238c42d"
movie_title="Eternals"
# header={
#      "api_key":API_KEY
#  }

# parameters= {
#
#     "api_key": API_KEY,
#     "language": "en-US"
#     "query": movie_title
#  }
response = requests.get(url=API_URL, params={"api_key": API_KEY, "query": movie_title})
response.raise_for_status()
data = response.json()
print(data)
