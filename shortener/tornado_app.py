import json
import os

from tornado import web, httpserver, ioloop, options
from validators.url import url as validate_url
from storage import InMemoryStorage

storage = InMemoryStorage()
PORT = 8000
host = '127.0.0.1:8000/'


class ShortenUrlHandler(web.RequestHandler):
    def post(self):
        url = json.loads(self.request.body)['url']
        if not '://' in url:
            url = 'http://' + url
        if not validate_url(url):
            self.write({'error': 'Invalid url'})
        else:
            key = storage.insert(url)
            self.write({'short_url': host + key})


class RedirectToOriginalHandler(web.RequestHandler):
    def get(self, url_id):
        url = storage.retrieve(url_id.encode('ascii'))
        if url == None:
            self.send_error(404)
        self.redirect(url)


urls = [
    (r"/shorten_url", ShortenUrlHandler),
    (r"/(.*)", RedirectToOriginalHandler)
]

application = web.Application(urls)

if __name__ == "__main__":
    server = httpserver.HTTPServer(application)
    server.listen(PORT)
    ioloop.IOLoop.instance().start()
