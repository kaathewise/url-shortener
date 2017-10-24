import base64
import os
import struct
import sqlite3

class Storage:
    def __init__(self, path):
        self.path = path

    def __db_connect(self):
        return sqlite3.connect(self.path, timeout=10)

    def encode_id(self, id):
        return base64.urlsafe_b64encode(struct.pack('<Q', id))

    def decode_id(self, id):
        return struct.unpack('<Q', base64.urlsafe_b64decode(id))[0]

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
