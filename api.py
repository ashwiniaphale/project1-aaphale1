# pylint: disable=missing-module-docstring
# pylint: disable=line-too-long
# pylint: disable=trailing-whitespace
import os
import requests
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

BASE_URL = "https://api.themoviedb.org/3"

CONFIG_URL = BASE_URL + "/configuration" 

QUERY_PARAMS = {
    'api_key': os.getenv('API_KEY'),
}
CONFIG_RESPONSE = requests.get(CONFIG_URL, params=QUERY_PARAMS)
CONFIGURATION = CONFIG_RESPONSE.json()

def get_title(movie_id):
    '''returns title of movie'''
    movie_url = BASE_URL + "/movie/" + str(movie_id)
    movie_response = requests.get(movie_url, params=QUERY_PARAMS)
    return movie_response.json()["title"]

def get_tagline(movie_id):
    '''returns tagline of movie'''
    movie_url = BASE_URL + "/movie/" + str(movie_id)
    movie_response = requests.get(movie_url, params=QUERY_PARAMS)
    return movie_response.json()["tagline"]

def get_genre(movie_id):
    '''returns genres of movie after looping through list of dictionaries'''
    movie_url = BASE_URL + "/movie/" + str(movie_id)
    movie_response = requests.get(movie_url, params=QUERY_PARAMS)
    movie_genre = movie_response.json()["genres"]
    genres = ""
    for movie in movie_genre:
        genres = genres + str(movie['name']) + "," + " "
    genres = genres[:-2]
    return genres

def get_image(movie_id):
    '''uses configuration api and builds and returns movie poster image'''
    movie_url = BASE_URL + "/movie/" + str(movie_id)
    movie_response = requests.get(movie_url, params=QUERY_PARAMS)
    image_base_url = CONFIGURATION["images"]["base_url"]
    image_size = CONFIGURATION["images"]["poster_sizes"][4]
    final_url = image_base_url + "/" + image_size + movie_response.json()["poster_path"]
    return final_url

#used the sample code within the media wiki (API:Search)
def get_wiki_page(movie_id):
    '''uses wiki api:search to build the wikipedia full url and return wikipedia page'''
    session = requests.Session()

    wiki_base_url = "https://en.wikipedia.org/w/api.php"
    what_to_search = get_title(movie_id)

    params = {
        "action": "query",
        "format": "json",
        "list": "search",
        "srsearch": what_to_search
    }

    response = session.get(url=wiki_base_url, params=params)
    wiki_page = response.json()

    movie_title = wiki_page["query"]["search"][0]["title"]
    url_with_space = "https://en.wikipedia.org/wiki/" + movie_title
    return url_with_space.replace(" ", "_")
