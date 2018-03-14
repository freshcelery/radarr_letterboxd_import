"""
TMDB_Info class used as a storage container for info needed 
in order to add a new movie to Radarr.
"""

class TMDB_Info():

    def __init__(self, title, year, tvdb_id, poster_url):
        self.title = title
        self.year = year
        self.id = tvdb_id
        self.title_slug = '{}-{}'.format(self.title.replace(' ', '-'), self.id)
        self.poster_url = poster_url

    def __str__(self):
        return 'Title: %s, Year: %s, Id: %s, titleSlug: %s, Poster: %s' % (self.title, self.year, self.id, self.title_slug, self.poster_url)