import json
import tvdb_info
import requests
import os
from letterboxd import Letterboxd
from radarr import Radarr

class CommonFunctions():
    def __init__(self):
        self.letter = Letterboxd()
        self.radarr = Radarr()

    def write_to_json(self, movies, json_path):

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

    def letterboxd_thread(self, new_movies):
        letterboxd_movies = self.letter.get_watchlist()
        new_letterboxd_movies = self.letter.compare_movies_to_json(letterboxd_movies, self.letter.LETTERBOXD_JSON_PATH)

        new_movies = new_letterboxd_movies

    def radarr_thread(self):
        radarr_movies = self.radarr.get_movies()
        new_radarr_movies = self.radarr.compare_movies_to_json(radarr_movies)
        self.write_to_json(new_radarr_movies, self.radarr.RADARR_JSON_PATH)