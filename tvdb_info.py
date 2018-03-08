class TVDB_Info():

    def __init__(self, title, tvdb_id, poster_url):
        self.title = title
        self.id = tvdb_id
        self.title_slug = '{}-{}'.format(self.title.replace(' ', '-'), self.id)
        self.poster_url = poster_url

    def __str__(self):
        return 'Title: %s, Id: %s, titleSlug: %s, Poster: %s' % (self.title, self.id, self.title_slug, self.poster_url)