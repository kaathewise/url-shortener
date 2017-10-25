import os
import unittest
import tempfile
import shutil
import storage

from storage import SQLiteStorage, ShardedSQLiteStorage, InMemoryStorage, ShardedInMemoryStorage

class _StorageTestCase(object):
    def testInsertion(self):
        key = self.storage.insert('google.com')
        assert self.storage.retrieve(key) == 'google.com'
        assert self.storage.retrieve(storage.encode_id(12)) is None

    def testInsertMultiple(self):
        key1 = self.storage.insert('google.com')
        key2 = self.storage.insert('google.com')
        key3 = self.storage.insert('bit.ly')
        assert key1 != key2
        assert self.storage.retrieve(key2) == 'google.com'
        assert self.storage.retrieve(key3) == 'bit.ly'

    def testInvalidKey(self):
        self.storage.insert('google.com')
        assert self.storage.retrieve('invalid key') is None


class EncodingTest(unittest.TestCase):
    def testEncoding(self):
        assert storage.decode_id(storage.encode_id(1)) == 1
        assert storage.decode_id(storage.encode_id(4294967296)) == 4294967296


class SQLiteStorageTestCase(unittest.TestCase, _StorageTestCase):
    def setUp(self):
        self.storage_fd, self.storage_path = tempfile.mkstemp()
        self.storage = SQLiteStorage(self.storage_path)
        self.storage.init_db()

    def tearDown(self):
        os.close(self.storage_fd)
        os.unlink(self.storage_path)


class ShardedSQLiteStorageTestCase(unittest.TestCase, _StorageTestCase):
    def setUp(self):
        self.storage_path = tempfile.mkdtemp()
        self.storage = ShardedSQLiteStorage(self.storage_path + '/db')
        self.storage.init_db()

    def tearDown(self):
        shutil.rmtree(self.storage_path)


class ShardedInMemoryStorageTestCase(unittest.TestCase, _StorageTestCase):
    def setUp(self):
        self.storage = ShardedInMemoryStorage()


class InMemoryStorageTestCase(unittest.TestCase, _StorageTestCase):
    def setUp(self):
        self.storage = InMemoryStorage()


if __name__ == '__main__':
    unittest.main()
