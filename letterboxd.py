import tvdb_info
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
        self.LETTERBOXD_JSON_PATH = config.ConfigSectionMap('Letterboxd')['movie_storage_path']
    
    def get_watchlist(self):
        movies = []
        for username in self.LETTERBOXD_USERNAMES:
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

        return movies

    def compare_movies_to_json(self, movies, json_path):

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
        film_page_request = requests.get(letterboxd_url)
        soup = BeautifulSoup(film_page_request.text, 'html.parser')

        tmdb_element = soup.find('a', attrs={'data-track-action' : 'TMDb'})
        tmdb_url = tmdb_element.get('href')
        tmdb_id = (tmdb_url.split('/movie/',1)[1]).replace('/','')

        film_title_element = soup.find('h1', attrs={'itemprop' : 'name'})
        film_title = film_title_element.get_text()

        film_image_element = soup.find('img', attrs={'itemprop' : 'image'})
        film_image = film_image_element.get('src')

        tmdb_obj = tvdb_info.TVDB_Info(film_title, tmdb_id, film_image)

        return tmdb_obj