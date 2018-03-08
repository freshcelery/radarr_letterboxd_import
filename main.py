"""
Script for continously scraping one or many Letterboxd watchlists and adding
the movies found into Radarr if they do not already exist
"""
import json
import tvdb_info
import requests
import os
import sched
import time
from threading import Thread
from letterboxd import Letterboxd
from radarr import Radarr
from common_functions import CommonFunctions


def main():
    letter = Letterboxd()
    radarr = Radarr()
    common = CommonFunctions()
    
    letterboxd_movies = letter.get_watchlist()
    new_letterboxd_movies = letter.compare_movies_to_json(letterboxd_movies, letter.LETTERBOXD_JSON_PATH)

    radarr_movies = radarr.get_movies()
    new_radarr_movies = radarr.compare_movies_to_json(radarr_movies)
    common.write_to_json(new_radarr_movies, radarr.RADARR_JSON_PATH)

    new_movies = letter.compare_movies_to_json(new_letterboxd_movies, radarr.RADARR_JSON_PATH)
    new_movie_titles = []

    for movie in new_movies:
        radarr.add_movie_to_radarr(movie)
        new_movie_titles.append(movie.title)
    
    common.write_to_json(new_movie_titles, letter.LETTERBOXD_JSON_PATH)

if __name__ == '__main__':
    start_time = time.time()

    while True:
        main()
        time.sleep(600.0 - ((time.time() - start_time) % 60.0))