import json
import os
import shutil
import tempfile
import unittest

import app
from storage import SQLiteStorage, ShardedSQLiteStorage, InMemoryStorage, ShardedInMemoryStorage

class _AppTestCase(object):
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


class SQLiteAppTestCase(unittest.TestCase, _AppTestCase):
    def setUp(self):
        self.storage_fd, self.storage_path = tempfile.mkstemp()
        self.storage = SQLiteStorage(self.storage_path)
        self.storage.init_db()
        self.client = app.app.test_client()
        self.client.testing = True
        app.storage = self.storage

    def tearDown(self):
        os.close(self.storage_fd)
        os.unlink(self.storage_path)


class ShardedSQLiteStorageTestCase(unittest.TestCase, _AppTestCase):
    def setUp(self):
        self.storage_path = tempfile.mkdtemp()
        self.storage = ShardedSQLiteStorage(self.storage_path + '/db')
        self.storage.init_db()
        self.client = app.app.test_client()
        self.client.testing = True
        app.storage = self.storage

    def tearDown(self):
        shutil.rmtree(self.storage_path)


class ShardedInMemoryStorageTestCase(unittest.TestCase, _AppTestCase):
    def setUp(self):
        self.storage = ShardedInMemoryStorage()
        self.client = app.app.test_client()
        self.client.testing = True
        app.storage = self.storage


class InMemoryStorageTestCase(unittest.TestCase, _AppTestCase):
    def setUp(self):
        self.storage = InMemoryStorage()
        self.client = app.app.test_client()
        self.client.testing = True
        app.storage = self.storage


if __name__ == '__main__':
    unittest.main()
