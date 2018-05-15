"""
Script for continously scraping one or many Letterboxd watchlists and adding
the movies found into Radarr if they do not already exist
"""

import sched
import time
from letterboxd_watchlist import Letterboxd_Watchlist
from letterboxd_helpers import Letterboxd_Helpers
from letterboxd_lists import Letterboxd_Lists
from radarr import Radarr


def main():
    letterboxd_watchlist = Letterboxd_Watchlist()
    letterboxd_lists = Letterboxd_Lists()
    letterboxd_helpers = Letterboxd_Helpers()
    radarr = Radarr()
    
    radarr_movies = radarr.get_movies()
    new_radarr_movies = radarr.compare_movies_to_json(radarr_movies)
    radarr.write_to_json(new_radarr_movies)

    letterboxd_watchlist_movies = letterboxd_watchlist.get_watchlist()
    letterboxd_list_movies = letterboxd_lists.get_lists()
    letterboxd_movies = list(set(letterboxd_watchlist_movies + letterboxd_list_movies))
    new_movies = letterboxd_helpers.compare_movies_to_json(letterboxd_movies, radarr.RADARR_JSON_PATH)
    new_movie_titles = []
    for movie in new_movies:
        print("Adding Movie: {}".format(movie.title))
        radarr.add_movie_to_radarr(movie)
        new_movie_titles.append(movie.title)
        
    radarr.write_to_json(new_movie_titles)
if __name__ == '__main__':
    start_time = time.time()

    while True:
        print("Scanning for new movies")
        main()
        print("Scanning complete")
        time.sleep(6000.0 - ((time.time() - start_time) % 60.0))