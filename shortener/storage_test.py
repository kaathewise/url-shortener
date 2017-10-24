import os
import unittest
import tempfile

from storage import Storage

class StorageTestCase(unittest.TestCase):
    def setUp(self):
        self.storage_fd, self.storage_path = tempfile.mkstemp()
        self.storage = Storage(self.storage_path)

    def tearDown(self):
        os.close(self.storage_fd)
        os.unlink(self.storage_path)

    def testEncoding(self):
        assert self.storage.decode_id(self.storage.encode_id(1)) == 1
        assert self.storage.decode_id(self.storage.encode_id(4294967296)) == 4294967296

    def testInsertion(self):
        self.storage.init_db()
        key = self.storage.insert('google.com')
        assert self.storage.retrieve(key) == 'google.com'
        assert self.storage.retrieve(self.storage.encode_id(12)) is None

    def testInsertMultiple(self):
        self.storage.init_db()
        key1 = self.storage.insert('google.com')
        key2 = self.storage.insert('google.com')
        key3 = self.storage.insert('bit.ly')
        assert key1 != key2
        assert self.storage.retrieve(key2) == 'google.com'
        assert self.storage.retrieve(key3) == 'bit.ly'

    def testInvalidKey(self):
        self.storage.init_db()
        self.storage.insert('google.com')
        assert self.storage.retrieve('invalid key') is None

if __name__ == '__main__':
    unittest.main()
