import tvdb_info
import requests
import json
import os
from bs4 import BeautifulSoup
from config_mapper import ConfigParse

class Radarr():

    def __init__(self):
        config = ConfigParse('config.ini')

        self.RADARR_JSON_PATH = config.ConfigSectionMap('Radarr')['movie_storage_path']
        self.RADARR_API_KEY = config.ConfigSectionMap('Radarr')['api_key']
        self.RADARR_API_URL = config.ConfigSectionMap('Radarr')['api_url']
        self.RADARR_QUALITY_PROFILE = config.ConfigSectionMap('Radarr')['quality_profile']
        self.RADARR_ROOT_PATH = config.ConfigSectionMap('Radarr')['root_folder_path']
    
    def get_movies(self):
        radarr_movie_titles = []

        radarr_get_url = '{}/api/movie?apikey={}'.format(self.RADARR_API_URL, self.RADARR_API_KEY)
        radarr_page_request = requests.get(radarr_get_url)
        radarr_movies_json = radarr_page_request.json()

        for movie in radarr_movies_json:
            movie_title = json.dumps(movie['title'])
            movie_title = movie_title.replace('"','')
            radarr_movie_titles.append(movie_title)

        return radarr_movie_titles

    def compare_movies_to_json(self, movies):

        if os.path.exists(self.RADARR_JSON_PATH):
            with open(self.RADARR_JSON_PATH, 'r') as outfile:
                saved_movies = json.load(outfile)

            new_movies = []

            for i in movies:
                if i not in saved_movies:
                    new_movies.append(i)

            return new_movies
        else:
            return movies

    def add_movie_to_radarr(self, tvdb_info):
    
        payload = {
            'title': tvdb_info.title,
            'year': tvdb_info.year,
            'qualityProfileId': self.RADARR_QUALITY_PROFILE,
            'rootFolderPath': self.RADARR_ROOT_PATH,
            'tmdbId': tvdb_info.id,
            'titleSlug': tvdb_info.title_slug,
            'images': [{'covertype':'poster','url':'{}'.format(tvdb_info.poster_url)}],
            'addOptions' : {
                'searchForMovie' : 'true'
            }
        }
    
        requests.post('{}/api/movie?apikey={}'.format(self.RADARR_API_URL, self.RADARR_API_KEY), data=json.dumps(payload))
    
    def write_to_json(self, movies):

        if os.path.exists(self.RADARR_JSON_PATH):
            with open(self.RADARR_JSON_PATH) as outfile:
                data = json.load(outfile)

            data.extend(movies)

            with open(self.RADARR_JSON_PATH, 'w') as outfile:
                json.dump(data, outfile)
    
        else:
            with open(self.RADARR_JSON_PATH, 'w') as outfile:
                json.dump(movies, outfile)

        outfile.close()