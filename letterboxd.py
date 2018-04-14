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
from log import log_to_file

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
                requests.get('https://letterboxd.com/' + username + '/watchlist/')
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
                            film_page_request = requests.get(letterboxd_film_url, allow_redirects=False)
                            if (film_page_request.status_code in [200,201,202,203,204,205,206]):
                                tmdb_obj = self.create_tmdb_obj(film_page_request)
                                movies.append(tmdb_obj)
                            else:
                                log_to_file("{} was unavailable".format(letterboxd_film_url, allow_redirects=False))
                else:
                    for frame_title in soup.find_all('div', class_='film-poster'):
                        letterboxd_url_sub = frame_title.get('data-film-slug')
                        letterboxd_film_url = 'https://letterboxd.com{}'.format(letterboxd_url_sub)
                        tmdb_obj = self.create_tmdb_obj(letterboxd_film_url)
                        movies.append(tmdb_obj)
            except Exception as e:
                log_to_file('There was an error retrieving films from Letterboxd: {0} \n'.format(e))
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

    def create_tmdb_obj(self, letterboxd_response):
        """Create TMDB_Info objects from info parsed from a letterboxd movie page."""
        try:
            soup = BeautifulSoup(letterboxd_response.text, 'html.parser')

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
        except TypeError as e:
            log_to_file('TypeError while creating tmdb_obj: {0} \n'.format(e))
        except Exception as e:
            log_to_file('Failure while creating tmdb_obj: {0} \n'.format(e))
            log_to_file('Exception Args: {0}'.format(e.args))
            raise Exception('Failure while creating tmdb_obj')
