import json
import os

from tornado import gen, web, httpserver, ioloop, process
from validators.url import url as validate_url
from storage import RedisStorage, encode_id

host = '127.0.0.1:8000/'
PORT = 8000
num_tasks = 16

next_id = 0
def get_next_id():
    global next_id
    next_id += num_tasks
    return next_id - process.task_id()


class ShortenUrlHandler(web.RequestHandler):
    @gen.coroutine
    def post(self):
        url = json.loads(self.request.body)['url']
        if not '://' in url:
            url = 'http://' + url
        if not validate_url(url):
            self.write({'error': 'Invalid url'})
        else:
            key = encode_id(get_next_id())
            yield storage.insert(url, key)
            self.write({'short_url': host + key})


class RedirectToOriginalHandler(web.RequestHandler):
    @gen.coroutine
    def get(self, url_id):
        url = yield storage.retrieve(url_id.encode('ascii'))
        if url == None:
            self.send_error(404)
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
    storage = RedisStorage('localhost', 6379)
    ioloop.IOLoop.current().start()
