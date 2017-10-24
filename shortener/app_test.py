import json
import os
import tempfile
import unittest

import app

class AppTestCase(unittest.TestCase):
    def setUp(self):
        self.storage_fd, self.storage_path = tempfile.mkstemp()
        app.app.config['DATABASE'] = self.storage_path
        self.client = app.app.test_client()
        self.client.testing = True
        app.init()
        app.storage.init_db()

    def tearDown(self):
        os.close(self.storage_fd)
        os.unlink(self.storage_path)

    def testShortenUrl(self):
        response = self.client.post('/shorten_url',
                data=json.dumps(dict(url='google.com')))
        short_url = json.loads(response.data)['short_url']
        assert short_url
        response = self.client.get(short_url.split('/')[1])
        assert response.status_code == 302
        assert 'google.com' in response.location

    def testInvalidRequests(self):
        response = self.client.post('/shorten_url', data=json.dumps(dict(url='')))
        assert json.loads(response.data)['error']
        response = self.client.get('/abcdef')
        assert response.status_code == 404
        response = self.client.get('/.++')
        assert response.status_code == 404

if __name__ == '__main__':
    unittest.main()
