"""
"""
import tmdb_info
import requests
import os
import json
from bs4 import BeautifulSoup
from log import log_to_file

class Letterboxd_Helpers():
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
            if 'tv' in tmdb_url:
                return None    
            else:
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
            log_to_file('Exception Args: {0} \n'.format(e.args))
            raise Exception('Failure while creating tmdb_obj')
