"""
Script for continously scraping one or many Letterboxd watchlists and adding
the movies found into Radarr if they do not already exist
"""
import json
import os
import tvdb_info
import requests
from bs4 import BeautifulSoup
from config_mapper import ConfigParse

config = ConfigParse('config.ini')

LETTERBOXD_USERNAMES_PREFORMATED = config.ConfigSectionMap('Letterboxd')['usernames']
LETTERBOXD_USERNAMES = LETTERBOXD_USERNAMES_PREFORMATED.split()
LETTERBOXD_JSON_PATH = config.ConfigSectionMap('Letterboxd')['movie_storage_path']

RADARR_JSON_PATH = config.ConfigSectionMap('Radarr')['movie_storage_path']
RADARR_API_KEY = config.ConfigSectionMap('Radarr')['api_key']
RADARR_API_URL = config.ConfigSectionMap('Radarr')['api_url']
RADARR_QUALITY_PROFILE = config.ConfigSectionMap('Radarr')['quality_profile']
RADARR_ROOT_PATH = config.ConfigSectionMap('Radarr')['root_folder_path']

TVDB_API_KEY = config.ConfigSectionMap('TVDB')['api_key']

def get_watchlist():
    movies = []
    for username in LETTERBOXD_USERNAMES:
        letterboxd_page_req = requests.get('https://letterboxd.com/' + username + '/watchlist/')
        soup = BeautifulSoup(letterboxd_page_req.text , 'html.parser')

        if(soup.find_all(class_='paginate-page')):
            num_of_pages = len(soup.find_all(class_='paginate-page'))

            for page_num in range(1, num_of_pages + 1):
                page_request = requests.get('https://letterboxd.com/{}/watchlist/page/{}'.format(username, page_num))
                page_soup = BeautifulSoup(page_request.text, 'html.parser')

                for frame_title in page_soup.find_all('div', class_='film-poster'):
                    image_element = frame_title.find('img')
                    movie_title = image_element.get('alt')
                    movies.append(movie_title)
        else:
            for frame_title in soup.find_all('div', class_='film-poster'):
                image_element = frame_title.find('img')
                movie_title = image_element.get('alt')
                movies.append(movie_title)

    return movies

def compare_movies_to_json(movies):
    global LETTERBOXD_JSON_PATH

    if os.path.exists(LETTERBOXD_JSON_PATH):
        with open(LETTERBOXD_JSON_PATH, 'r') as outfile:
            saved_movies = json.load(outfile)
        
        for i in movies:
            if i in saved_movies:
                movies.remove(i)
        
    return movies

def write_to_json(movies, json_path):

    if os.path.exists(json_path):
        with open(json_path) as outfile:
            data = json.load(outfile)

        data.extend(movies)

        with open(json_path, 'w') as outfile:
            json.dump(data, outfile)
    
    else:
        with open(json_path, 'w') as outfile:
            json.dump(movies, outfile)

    outfile.close()

def query_radarr_for_movies():
    radarr_movie_titles = []

    radarr_get_url = '{}/api/movie?apikey={}'.format(RADARR_API_URL, RADARR_API_KEY)
    radarr_page_request = requests.get(radarr_get_url)
    radarr_movies_json = radarr_page_request.json()

    for movie in radarr_movies_json:
        movie_title = json.dumps(movie['title'])
        movie_title = movie_title.replace('"','')
        radarr_movie_titles.append(movie_title)

    return radarr_movie_titles

def get_tvdb_info(movie_title):
    tvdb_url = 'https://api.themoviedb.org/3/search/movie?query={}&api_key={}'.format(movie_title, TVDB_API_KEY)
    tvdb_page_request = requests.get(tvdb_url)
    tvdb_result_json = tvdb_page_request.json()

    movie_title = tvdb_result_json['results'][0]['title']
    movie_id = tvdb_result_json['results'][0]['id']
    movie_poster_path = 'http://image.tmdb.org/t/p/w185/{}'.format(tvdb_result_json['results'][0]['poster_path'])

    tvdb_movie = tvdb_info.TVDB_Info(movie_title, movie_id, movie_poster_path)

    return tvdb_movie


def add_movie_to_radarr(tvdb_info):
    
    payload = {
        'title': tvdb_info.title,
        'qualityProfileId': RADARR_QUALITY_PROFILE,
        'rootFolderPath': RADARR_ROOT_PATH,
        'tmdbId': tvdb_info.id,
        'titleSlug': tvdb_info.title_slug,
        'images': [{'covertype':'poster','url':'{}'.format(tvdb_info.poster_url)}]
    }
    
    requests.post('{}/api/movie?apikey={}'.format(RADARR_API_URL, RADARR_API_KEY), data=json.dumps(payload))

if __name__ == '__main__':
    movies = get_watchlist()

    movies_to_add = compare_movies_to_json(movies)

    write_to_json(movies_to_add, LETTERBOXD_JSON_PATH)

    radarr_movies = query_radarr_for_movies()

    write_to_json(radarr_movies, RADARR_JSON_PATH)
    
    new_movies = set(movies_to_add) - set(radarr_movies)
    print(new_movies)

"""
    for movie in new_movies:
        tvdb_movie = get_tvdb_info(movie)
        add_movie_to_radarr(tvdb_movie)
"""