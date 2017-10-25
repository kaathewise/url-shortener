import tornado.web
import tornado.httpserver
import tornado.ioloop
from tornado.options import define, options
from tornado.process import task_id
import json
import os
from urlparse import urlparse
from storage import RedisStorage, encode_id

define("port", default=8000, type=int)
host = '127.0.0.1:8000/'
num_tasks = 16

counter = 0

def get_next_id():
    global counter
    counter += num_tasks
    return counter - task_id()


class ShortenUrlHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def post(self):
        url = json.loads(self.request.body)['url']
        parsed_url = urlparse(url, 'http')
        if not parsed_url.netloc and not parsed_url.path:
            self.write({'error': 'Invalid url'})
        else:
            key = encode_id(get_next_id())
            yield storage.insert(parsed_url.geturl(), key)
            self.write({'short_url': host + key})


class RedirectToOriginalHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self, url_id):
        url = yield storage.retrieve(url_id.encode('ascii'))
        if url == None:
            abort(404)
        self.redirect(url)


urls = [
    (r"/shorten_url", ShortenUrlHandler),
    (r"/(.*)", RedirectToOriginalHandler)
]

def make_app():
    return tornado.web.Application(urls)


if __name__ == "__main__":
    server = tornado.httpserver.HTTPServer(make_app())
    server.bind(options.port)
    server.start(num_tasks)
    storage = RedisStorage('localhost', 6379)
    tornado.ioloop.IOLoop.current().start()
