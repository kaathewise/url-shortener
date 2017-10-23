#!/usr/bin/env python

DATABASE = 'storage.db'

def db_connect():
  return sqlite3.connect(DATABASE)

class Storage:
    def init_db():
      with db_connect() as conn:
          with app.open_resource('schema.sql', mode='r') as f:
              conn.cursor().executescript(f.read())

    def insert(url):
        with db_connect() as conn:
            cursor = conn.cursor()
            res = cursor.execute(
                'INSERT INTO URL (BASE_URL) VALUES (?);', [url])
        return base64.urlsafe_b64encode(res.lastrowid)

    def retrieve(id):
        id = int(base64.urlsafe_b64decode(id))
        with db_connect() as conn:
            cursor = conn.cursor()
            res = cursor.execute('SELECT BASE_URL FROM URL WHERE ID=?;', [id])
            try:
                return res.fetchone()
            except Exception as e:
                print(e)
                return None
