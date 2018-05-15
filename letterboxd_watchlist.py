"""
Letterboxd class used for parsing letterboxd watchlists
and creating TMDB(The Movie Database) objects for sending to Radarr.
"""

import tmdb_info
import requests
import os
import json
from letterboxd_helpers import Letterboxd_Helpers
from bs4 import BeautifulSoup
from config_mapper import ConfigParse
from log import log_to_file

class Letterboxd_Watchlist():

    def __init__(self):
        config = ConfigParse('config.ini')

        self.LETTERBOXD_USERNAMES_PREFORMATED = config.ConfigSectionMap('Letterboxd')['usernames']
        self.LETTERBOXD_USERNAMES = self.LETTERBOXD_USERNAMES_PREFORMATED.split()
        self.helpers = Letterboxd_Helpers()
    
    def get_watchlist(self):
        """ Grab all movies from watchlists and return in an array of tmdb_info objects."""

        movies = []
        for username in self.LETTERBOXD_USERNAMES:
            try:
                letterboxd_page_req = requests.get('https://letterboxd.com/' + username + '/watchlist/')
                soup = BeautifulSoup(letterboxd_page_req.text , 'html.parser')

                if(soup.find_all(class_='paginate-page')):
                    pages = soup.find_all(class_='paginate-page')
                    for page_element in pages:pass
                    if page_element :
                        num_of_pages = int(page_element .getText())
                    else:
                        num_of_pages = len(pages)

                    for page_num in range(1, num_of_pages + 1):
                        page_request = requests.get('https://letterboxd.com/{}/watchlist/page/{}'.format(username, page_num))
                        page_soup = BeautifulSoup(page_request.text, 'html.parser')

                        for frame_title in page_soup.find_all('div', class_='film-poster'):
                            letterboxd_url_sub = frame_title.get('data-film-slug')
                            letterboxd_film_url = 'https://letterboxd.com{}'.format(letterboxd_url_sub)
                            film_page_request = requests.get(letterboxd_film_url, allow_redirects=False)
                            if (film_page_request.status_code in [200,201,202,203,204,205,206]):
                                tmdb_obj = self.helpers.create_tmdb_obj(film_page_request)
                                if(tmdb_obj):
                                    movies.append(tmdb_obj)
                            else:
                                log_to_file("{} was unavailable \n".format(letterboxd_film_url, allow_redirects=False))
                else:
                    for frame_title in soup.find_all('div', class_='film-poster'):
                        letterboxd_url_sub = frame_title.get('data-film-slug')
                        letterboxd_film_url = 'https://letterboxd.com{}'.format(letterboxd_url_sub)
                        film_page_request = requests.get(letterboxd_film_url, allow_redirects=False)
                        tmdb_obj = self.helperscreate_tmdb_obj(film_page_request)
                        if(tmdb_obj):
                            movies.append(tmdb_obj)
            except Exception as e:
                log_to_file('There was an error retrieving films from Letterboxd: {0} \n'.format(e))
                raise Exception('There was an error retrieving films from Letterboxd')
        return movies