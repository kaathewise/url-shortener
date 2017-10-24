import base64
import os
import struct
import sqlite3
import threading

from random import randint

class IntKeyedStorage:
    def encode_id(self, id):
        return base64.urlsafe_b64encode(struct.pack('<Q', id))

    def decode_id(self, id):
        return struct.unpack('<Q', base64.urlsafe_b64decode(id))[0]


class SQLiteStorage(IntKeyedStorage):
    def __init__(self, path):
        self.path = path

    def __db_connect(self):
        return sqlite3.connect(self.path, timeout=10)

    def init_db(self):
      with self.__db_connect() as conn:
          with open(os.path.dirname(__file__)+'/schema.sql', mode='r') as f:
              conn.cursor().executescript(f.read())

    def insert(self, url):
        with self.__db_connect() as conn:
            cursor = conn.cursor()
            res = cursor.execute(
                'INSERT INTO URL (BASE_URL) VALUES (?);', [url])
            return self.encode_id(res.lastrowid)

    def retrieve(self, id):
        try:
            id = self.decode_id(id)
        except:
            return None
        with self.__db_connect() as conn:
            cursor = conn.cursor()
            res = cursor.execute('SELECT BASE_URL FROM URL WHERE ID=?;', [id]).fetchone()
            return res[0] if res else None


class ShardedSQLiteStorage(IntKeyedStorage):
    def __init__(self, base_path, shards=64):
        self.base_path = base_path
        self.shards = shards

    def __db_connect(self, shard):
        return sqlite3.connect(self.base_path + str(shard), timeout=10)

    def init_db(self):
      for shard in xrange(self.shards):
          with self.__db_connect(shard) as conn:
              with open(os.path.dirname(__file__)+'/schema.sql', mode='r') as f:
                  conn.cursor().executescript(f.read())

    def insert(self, url):
        shard = randint(0, self.shards-1)
        with self.__db_connect(shard) as conn:
            cursor = conn.cursor()
            res = cursor.execute(
                'INSERT INTO URL (BASE_URL) VALUES (?);', [url])
            return self.encode_id(res.lastrowid * self.shards + shard)

    def retrieve(self, id):
        try:
            id = self.decode_id(id)
        except:
            return None
        shard = id % self.shards
        id = id // self.shards
        with self.__db_connect(shard) as conn:
            cursor = conn.cursor()
            res = cursor.execute('SELECT BASE_URL FROM URL WHERE ID=?;', [id]).fetchone()
            return res[0] if res else None


class InMemoryStorage(IntKeyedStorage):
    def __init__(self):
        self.db = []

    def init_db(self):
        pass

    def insert(self, url):
        self.db.append(url)
        rowid = len(self.db) - 1
        return self.encode_id(rowid)

    def retrieve(self, id):
        try:
            id = self.decode_id(id)
        except:
            return None
        return self.db[id] if len(self.db) > id else None


class ShardedInMemoryStorage(IntKeyedStorage):
    def __init__(self, shards=128):
        self.shards = shards
        self.locks = [threading.Lock() for x in xrange(shards)]
        self.db = [[] for i in xrange(shards)]

    def init_db(self):
        pass

    def insert(self, url):
        shard = randint(0, self.shards-1)
        with self.locks[shard]:
            self.db[shard].append(url)
            rowid = len(self.db[shard]) - 1
            return self.encode_id(rowid * self.shards + shard)

    def retrieve(self, id):
        try:
            id = self.decode_id(id)
        except:
            return None
        shard = id % self.shards
        id = id // self.shards
        return self.db[shard][id] if len(self.db[shard]) > id else None
