from flask import Flask, abort, request, redirect, jsonify
from urlparse import urlparse

import storage as storage_module

host = None
storage = None
app = Flask(__name__)

@app.route('/shorten_url', methods=['POST'])
def shorten_url():
    url = request.get_json(force=True)['url']
    parsed_url = urlparse(url, 'http')
    if not parsed_url.netloc and not parsed_url.path:
        return jsonify(error = 'Invalid url')
    key = storage.insert(parsed_url.geturl())
    return jsonify(short_url = host + '/' + key)


@app.route('/<url_id>')
def redirect_to_original(url_id):
    url = storage.retrieve(url_id.encode('ascii'))
    if url == None:
        abort(404)
    return redirect(url)


if __name__ == '__main__':
    app.config.from_envvar('SHRT_CONFIG')
    storage = app.config['STORAGE']
    host = app.config['SERVER_NAME']
    app.run(threaded=app.config['THREADED'])
