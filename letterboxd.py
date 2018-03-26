"""
Letterboxd class used for parsing letterboxd watchlists
and creating TMDB(The Movie Database) objects for sending to Radarr.
"""

import tmdb_info
import requests
import os
import json
from bs4 import BeautifulSoup
from config_mapper import ConfigParse

class Letterboxd():

    def __init__(self):
        config = ConfigParse('config.ini')

        self.LETTERBOXD_USERNAMES_PREFORMATED = config.ConfigSectionMap('Letterboxd')['usernames']
        self.LETTERBOXD_USERNAMES = self.LETTERBOXD_USERNAMES_PREFORMATED.split()
    
    def get_watchlist(self):
        """ Grab all movies from watchlists and return in an array of tmdb_info objects."""

        movies = []
        for username in self.LETTERBOXD_USERNAMES:
            try:
                letterboxd_page_req = requests.get('https://letterboxd.com/' + username + '/watchlist/')
                soup = BeautifulSoup(letterboxd_page_req.text , 'html.parser')

                if(soup.find_all(class_='paginate-page')):
                    num_of_pages = len(soup.find_all(class_='paginate-page'))

                    for page_num in range(1, num_of_pages + 1):
                        page_request = requests.get('https://letterboxd.com/{}/watchlist/page/{}'.format(username, page_num))
                        page_soup = BeautifulSoup(page_request.text, 'html.parser')

                        for frame_title in page_soup.find_all('div', class_='film-poster'):
                            letterboxd_url_sub = frame_title.get('data-film-slug')
                            letterboxd_film_url = 'https://letterboxd.com{}'.format(letterboxd_url_sub)
                            tmdb_obj = self.create_tmdb_obj(letterboxd_film_url)
                            movies.append(tmdb_obj)
                else:
                    for frame_title in soup.find_all('div', class_='film-poster'):
                        letterboxd_url_sub = frame_title.get('data-film-slug')
                        letterboxd_film_url = 'https://letterboxd.com{}'.format(letterboxd_url_sub)
                        tmdb_obj = self.create_tmdb_obj(letterboxd_film_url)
                        movies.append(tmdb_obj)
            except:
                raise Exception('There was an error retrieving films from Letterboxd')
        return movies

    def compare_movies_to_json(self, movies, json_path):
        """Compare an array of TMDB_Info object titles to movies stored in JSON."""

        if os.path.exists(json_path):
            with open(json_path, 'r') as outfile:
                saved_movies = json.load(outfile)
        
            new_movies = []
            for i in movies:
                if i.title not in saved_movies:
                    new_movies.append(i)
            
            return new_movies

        else:
            return movies

    def create_tmdb_obj(self, letterboxd_url):
        """Create TMDB_Info objects from info parsed from a letterboxd movie page."""
        film_page_request = requests.get(letterboxd_url)
        soup = BeautifulSoup(film_page_request.text, 'html.parser')

        tmdb_element = soup.find('a', attrs={'data-track-action' : 'TMDb'})
        tmdb_url = tmdb_element.get('href')
        tmdb_id = (tmdb_url.split('/movie/',1)[1]).replace('/','')

        film_title_element = soup.find('h1', attrs={'itemprop' : 'name'})
        film_title = film_title_element.get_text()

        film_image_element = soup.find('img', attrs={'itemprop' : 'image'})
        film_image = film_image_element.get('src')

        date_published_element = soup.find('small', attrs={'itemprop' : 'datePublished'})
        date_anchor = date_published_element.find('a')
        film_published_date = date_anchor.get_text()

        tmdb_obj = tmdb_info.TMDB_Info(film_title, film_published_date, tmdb_id, film_image)

        return tmdb_obj