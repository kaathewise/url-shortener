from flask import Flask, abort, request, redirect, jsonify
from urlparse import urlparse

from storage import Storage

DATABASE = 'storage.db'
host = '127.0.0.1:5000/'

app = Flask(__name__)
app.config.from_object(__name__)

storage = Storage(app.config['DATABASE'])

@app.route('/shorten_url', methods=['POST'])
def shorten_url():
    url = request.get_json(force=True)['url']
    parsed_url = urlparse(url)
    if not parsed_url.scheme:
        url = 'http://' + url
    key = storage.insert(url)
    return jsonify(short_url = host + key)


@app.route('/<url_id>')
def redirect_to_original(url_id):
    url = storage.retrieve(url_id)
    if url == None:
        abort(404)
    return redirect(url.encode('utf-8'))


if __name__ == '__main__':
    app.run()
