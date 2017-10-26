import json
import os

from tornado import gen, web, httpserver, ioloop, process
from validators.url import url as validate_url
from storage import RedisStorage

host = '127.0.0.1:8000/'
PORT = 8000
num_tasks = 16

class ShortenUrlHandler(web.RequestHandler):
    @gen.coroutine
    def post(self):
        url = json.loads(self.request.body)['url']
        if not '://' in url:
            url = 'http://' + url
        if not validate_url(url):
            self.write({'error': 'Invalid url'})
        else:
            key = yield storage.insert(url)
            self.write({'short_url': host + key})


class RedirectToOriginalHandler(web.RequestHandler):
    @gen.coroutine
    def get(self, url_id):
        url = yield storage.retrieve(url_id)
        if url == None:
            self.send_error(404)
        else:
            self.redirect(url)


urls = [
    (r"/shorten_url", ShortenUrlHandler),
    (r"/(.*)", RedirectToOriginalHandler)
]

def make_app():
    return web.Application(urls)

if __name__ == "__main__":
    server = httpserver.HTTPServer(make_app())
    server.bind(PORT)
    server.start(num_tasks)
    storage = RedisStorage('localhost', 6379, num_tasks)
    ioloop.IOLoop.current().start()
