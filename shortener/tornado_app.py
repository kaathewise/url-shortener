import tornado.web
import tornado.httpserver
import tornado.ioloop
from tornado.options import define, options
import json
import os
from urlparse import urlparse
from storage import InMemoryStorage

storage = InMemoryStorage()
define("port", default=8000, type=int)
host = '127.0.0.1:8000/'


class ShortenUrlHandler(tornado.web.RequestHandler):
    def post(self):
        url = json.loads(self.request.body)['url']
        parsed_url = urlparse(url, 'http')
        if not parsed_url.netloc and not parsed_url.path:
            self.write({'error': 'Invalid url'})
            return
        key = storage.insert(parsed_url.geturl())
        self.write({'short_url': host + key})


class RedirectToOriginalHandler(tornado.web.RequestHandler):
    def get(self, url_id):
        url = storage.retrieve(url_id.encode('ascii'))
        if url == None:
            abort(404)
        return self.redirect(url)


urls = [
    (r"/shorten_url", ShortenUrlHandler),
    (r"/(.*)", RedirectToOriginalHandler)
]

settings = dict({
    "debug": False,
    "gzip": False,
})

application = tornado.web.Application(urls, **settings)


if __name__ == "__main__":
    server = tornado.httpserver.HTTPServer(application)
    server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
